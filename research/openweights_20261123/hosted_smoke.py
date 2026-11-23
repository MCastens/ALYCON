"""Pinned open-weight GPT-2 native causal-formation experiment.

Predict uses intact and single-head-removal trajectories. Reveal alone runs
the joint intervention. Exact-local + exact-tail is a diagnostic ceiling, NOT
a compute-matched forecast. Ordinary Python standard-library text only.
"""
import argparse, hashlib, importlib, json, math
from pathlib import Path
import numpy as np
import torch
from torch.func import jvp

ID="openai-community/gpt2"
REV="282e17ddc99feebb3443a5904dd65ac6d0b86055"
SHA="248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707"
DOCS=("ast","argparse","base64","bisect","difflib","statistics")
PAIRS=(((1,0),(5,1)),((2,2),(8,3)))
METHODS=("addition","tangent_head","finite_qkv","pade_norm","exact_local")

def digest(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()
def write(path,data):
    Path(path).write_text(json.dumps(data,sort_keys=True,indent=2,allow_nan=False)+"\n")
def load(path,download=False):
    path=Path(path)
    if download:
        from huggingface_hub import snapshot_download
        snapshot_download(repo_id=ID,revision=REV,local_dir=path,
          allow_patterns=["*.json","vocab.json","merges.txt","*.safetensors"])
    w=path/"model.safetensors"
    if not w.exists(): raise FileNotFoundError("Official pretrained weights missing: "+str(w))
    if digest(w)!=SHA: raise ValueError("Pretrained checkpoint SHA256 mismatch: "+digest(w))
    from transformers import GPT2LMHeadModel,AutoTokenizer
    model=GPT2LMHeadModel.from_pretrained(path,local_files_only=True,
           attn_implementation="eager",torch_dtype=torch.float32).eval()
    model.requires_grad_(False)
    tok=AutoTokenizer.from_pretrained(path,local_files_only=True)
    return model,tok
def readout(model,x):
    return model.lm_head(model.transformer.ln_f(x))
def trace(model,ids,remove=(),observe=None):
    blocks=model.transformer.h; d=model.config.n_embd//model.config.n_head
    states=[None]*(len(blocks)+1); native=[]; hooks=[]
    for l,b in enumerate(blocks):
        def grab(_,inp,l=l):states[l]=inp[0][0].detach().clone()
        hooks.append(b.register_forward_pre_hook(grab))
    hooks.append(model.transformer.ln_f.register_forward_pre_hook(
        lambda _,inp:states.__setitem__(-1,inp[0][0].detach().clone())))
    if observe is not None:
        hooks.append(blocks[observe].attn.c_proj.register_forward_pre_hook(
            lambda _,inp:native.append(inp[0][0].detach().clone())))
    for l,h in remove:
        def cut(_,inp,h=h):
            z=inp[0].clone();z[...,h*d:(h+1)*d]=0
            return (z,)
        hooks.append(blocks[l].attn.c_proj.register_forward_pre_hook(cut))
    try:
        with torch.no_grad():
            logits=model(ids[None],use_cache=False).logits[0].detach().clone()
    finally:
        for hook in hooks:hook.remove()
    assert all(x is not None for x in states)
    assert torch.allclose(readout(model,states[-1]),logits,atol=1e-4,rtol=0)
    return states,logits,native
def qkv(model,l,x,h):
    b=model.transformer.h[l];nh=model.config.n_head
    w=model.config.n_embd;d=w//nh
    return tuple(t.reshape(len(x),nh,d)[:,h,:] for t in b.attn.c_attn(b.ln_1(x)).split(w,-1))
def output(model,l,h,vecs,return_value=False):
    q,k,v=vecs
    s=q@k.T/(q.shape[-1]**.5)
    s=s.masked_fill(torch.ones_like(s,dtype=torch.bool).triu(1),-torch.inf)
    z=s.softmax(-1)@v
    if return_value:return z
    d=z.shape[-1]
    return z@model.transformer.h[l].attn.c_proj.weight[h*d:(h+1)*d]
def check_parity(model,l,x,native):
    z=torch.cat([output(model,l,h,qkv(model,l,x,h),True)
         for h in range(model.config.n_head)],-1)
    error=float((z-native).abs().max())
    if error>5e-5:raise AssertionError("QKV native pre-projection parity "+str(error))
    return error
def candidates(model,l,h,x,y):
    d=y-x
    b,t=jvp(lambda z:qkv(model,l,z,h),(x,),(d,))
    approx=tuple(a+v for a,v in zip(b,t))
    bh,dh=jvp(lambda z:output(model,l,h,qkv(model,l,z,h)),(x,),(d,))
    forms={"tangent_head":bh+dh,"finite_qkv":output(model,l,h,approx)}
    block=model.transformer.h[l]
    cx=x-x.mean(-1,keepdim=True);cy=y-y.mean(-1,keepdim=True);dc=cy-cx
    v0=cx.square().mean(-1,keepdim=True)+block.ln_1.eps
    t=(2*(cx*dc).mean(-1,keepdim=True)+dc.square().mean(-1,keepdim=True))/v0
    if ((1+.75*t).abs()<1e-6).any():raise ValueError("Invalid Pade denominator")
    normalized=cy*v0.rsqrt()*(1+.25*t)/(1+.75*t)
    w=model.config.n_embd;nh=model.config.n_head;hd=w//nh
    vals=block.attn.c_attn(normalized*block.ln_1.weight+block.ln_1.bias)
    vals=tuple(a.reshape(len(y),nh,hd)[:,h,:] for a in vals.split(w,-1))
    forms["pade_norm"]=output(model,l,h,vals)
    forms["exact_local"]=output(model,l,h,qkv(model,l,y,h))
    return forms,float(t.abs().median())
def suffix(model,l,y,h_est):
    b=model.transformer.h[l]
    actual_att=b.attn(b.ln_1(y[None]),use_cache=False)[0][0]
    u=y+actual_att-h_est
    u=u+b.mlp(b.ln_2(u[None]))[0]
    for j in range(l+1,model.config.n_layer):
        u=model.transformer.h[j](u[None],use_cache=False)[0][0]
    return readout(model,u)
def sources(tok):
    for name in DOCS:
        path=Path(importlib.import_module(name).__file__)
        ids=tok.encode(path.read_text(encoding="utf8"),add_special_tokens=False)
        if len(ids)<96:raise ValueError("Short source file "+name)
        yield name,digest(path),torch.tensor(ids[64:96],dtype=torch.long)
def predict(model_dir,out,download):
    out=Path(out);out.mkdir(parents=True,exist_ok=False)
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    model,tok=load(model_dir,download)
    rows=[]; arrays={}
    for name,source_hash,ids in sources(tok):
        c,zc,_=trace(model,ids)
        for pair in PAIRS:
            l,h=pair[1]
            a,za,internal=trace(model,ids,(pair[0],),observe=l)
            b,zb,_=trace(model,ids,(pair[1],))
            parity=check_parity(model,l,a[l],internal[0])
            forms,t=candidates(model,l,h,c[l],a[l])
            tag="case_"+str(len(rows))
            arrays[tag+"__addition"]=(za+zb-zc).numpy()
            for key,head in forms.items():
                arrays[tag+"__"+key]=suffix(model,l,a[l],head).detach().cpu().numpy()
            rows.append(dict(name=name,source_hash=source_hash,ids=ids.tolist(),
                        pair=pair,tag=tag,parity_error=parity,norm_change=t))
            print("PREDICT",name,pair,"parity",parity,flush=True)
    np.savez_compressed(out/"pred.npz",**arrays)
    meta=dict(model=ID,revision=REV,checkpoint_sha256=SHA,
        code_sha256=digest(__file__),prediction_sha256=digest(out/"pred.npz"),
        rows=rows,access="Observed clean + singleton trajectories only; local exact suffix costly and diagnostic",
        protocol="No joint intervention in predict. Only reveal calls both.")
    write(out/"freeze.json",meta)
    print("FREEZE",digest(out/"freeze.json"),flush=True)
def reveal(model_dir,out,freeze):
    out=Path(out);p=out/"freeze.json"
    if digest(p)!=freeze:raise ValueError("Freeze digest mismatch")
    meta=json.loads(p.read_text())
    if meta["code_sha256"]!=digest(__file__) or meta["prediction_sha256"]!=digest(out/"pred.npz"):
        raise ValueError("Code/predictions modified after freeze")
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    model,_=load(model_dir,False)
    pred=np.load(out/"pred.npz")
    scored=[]
    for row in meta["rows"]:
        _,joint,_=trace(model,torch.tensor(row["ids"]),tuple(map(tuple,row["pair"])))
        truth=joint.numpy();stats={}
        for method in METHODS:
            z=pred[row["tag"]+"__"+method]
            stats[method]=dict(sse=float(((z-truth)**2).sum()),
                  correct=int((z.argmax(-1)==truth.argmax(-1)).sum()))
        scored.append(dict(name=row["name"],pair=row["pair"],results=stats))
        print("REVEAL",row["name"],row["pair"],flush=True)
    summary={m:{k:sum(r["results"][m][k] for r in scored) for k in ("sse","correct")}
               for m in METHODS}
    write(out/"reveal.json",dict(freeze_sha256=freeze,model=ID,revision=REV,
      counts=dict(documents=len(DOCS),cases=len(scored),positions=len(scored)*32),
      results=scored,totals=summary,warning="Development-sized genuine pretrained model. Exact-local/suffix approximates joint computation and incurs extra model computation. No FLOP-matched advantage claim."))
    print("SUMMARY",json.dumps(summary),flush=True)
if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("phase",choices=["predict","reveal"])
    p.add_argument("--model-dir",default="weights/gpt2")
    p.add_argument("--out",default="results/gpt2")
    p.add_argument("--download",action="store_true")
    p.add_argument("--freeze-sha",default=None)
    a=p.parse_args()
    if a.phase=="predict":predict(a.model_dir,a.out,a.download)
    else:
        if not a.freeze_sha:p.error("--freeze-sha required")
        reveal(a.model_dir,a.out,a.freeze_sha)
