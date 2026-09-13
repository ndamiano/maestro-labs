"""Every verb of one character into ONE sheet, in the manifest lib/sprites.js already reads."""
import asyncio, base64, io, json, math, shutil, struct, sys
from pathlib import Path
import numpy as np
from playwright.async_api import async_playwright
from PIL import Image

DIRS = {"front":0.0, "right":math.pi/2, "back":math.pi, "left":3*math.pi/2}
CELL, FRAMES, FPS = 128, 8, 12

def active_window(path, keep=0.92):
    d=open(path,'rb').read(); n=struct.unpack('<I',d[12:16])[0]
    j=json.loads(d[20:20+n]); off=20+n+8
    def acc(i):
        a=j["accessors"][i]; v=j["bufferViews"][a["bufferView"]]
        o=off+v.get("byteOffset",0)+a.get("byteOffset",0)
        k={"VEC4":4,"VEC3":3,"SCALAR":1}[a["type"]]
        return np.frombuffer(d[o:o+a["count"]*k*4],dtype=np.float32).reshape(a["count"],k)
    anim=j["animations"][0]; speed=None; t=None
    for ch in anim["channels"]:
        s=anim["samplers"][ch["sampler"]]
        if ch["target"]["path"]!="rotation": continue
        t=acc(s["input"])[:,0]
        q=acc(s["output"]); q=q/np.linalg.norm(q,axis=1,keepdims=True)
        st=np.degrees(2*np.arccos(np.clip(np.abs(np.sum(q[1:]*q[:-1],axis=1)),-1,1)))
        speed = st if speed is None else speed+st
    cum=np.cumsum(speed); cum/=cum[-1]
    lo=int(np.searchsorted(cum,(1-keep)/2)); hi=int(np.searchsorted(cum,1-(1-keep)/2))
    return float(t[max(0,lo)]), float(t[min(len(t)-1,hi+1)])

async def main(pairs, out_png, out_json):
    view = Path("/home/nick/output/anim-still/mesh/view")
    clips = {}
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        for name, glb in pairs:
            shutil.copy(glb, view/"anim.glb")
            t0,t1 = active_window(glb)
            pg=await b.new_page(viewport={"width":300,"height":300})
            await pg.goto("http://127.0.0.1:8790/anim.html")
            await pg.wait_for_function("window.__ready===true", timeout=60000)
            for d,az in DIRS.items():
                ims=[]
                for i in range(FRAMES):
                    await pg.evaluate(f"window.__at({t0+(t1-t0)*i/(FRAMES-1)}); window.__view({az})")
                    data=await pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
                    ims.append(Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))).convert("RGBA"))
                clips[(name,d)]=ims
            await pg.close()
            print(f"  rendered {name} ({t0:.2f}-{t1:.2f}s)")
        await b.close()

    boxes=[im.split()[-1].getbbox() for ims in clips.values() for im in ims if im.split()[-1].getbbox()]
    x0=min(b[0] for b in boxes); y0=min(b[1] for b in boxes)
    x1=max(b[2] for b in boxes); y1=max(b[3] for b in boxes)
    cw=max(1,int(round((x1-x0)*CELL/(y1-y0))))
    rows=[(n,d) for n,_ in pairs for d in DIRS]
    sheet=Image.new("RGBA",(cw*FRAMES, CELL*len(rows)),(0,0,0,0))
    man={"cell":{"w":cw,"h":CELL},"dirs":list(DIRS),"anims":{},
         "pivot":{"x":cw/2.0,"y":CELL-4.0}}
    for r,(n,d) in enumerate(rows):
        man["anims"].setdefault(n,{"rows":{},"frames":FRAMES,"fps":FPS})["rows"][d]=r
        for i,im in enumerate(clips[(n,d)]):
            sheet.paste(im.crop((x0,y0,x1,y1)).resize((cw,CELL), Image.LANCZOS),(i*cw, r*CELL))
    sheet.save(out_png); Path(out_json).write_text(json.dumps(man))
    print(f"sheet {sheet.size}, cell {cw}x{CELL}, {len(rows)} rows -> {out_png}")

M="/home/nick/output/anim-still/matrix"
pairs=[("walk",f"{M}/tx_walk.glb"), ("idle",f"{M}/tx_idle.glb"),
       ("attack",f"{M}/txt_attack.glb"), ("defeat",f"{M}/tx_death.glb"),
       ("dodge",f"{M}/tx_dodge.glb"), ("hurt",f"{M}/tx_hurt.glb"),
       ("cast",f"{M}/tx_cast.glb")]
asyncio.run(main(pairs, sys.argv[1], sys.argv[2]))
