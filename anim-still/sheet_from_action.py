"""Sprite sheet from a retargeted glb: sample one cycle of its clip across four camera angles."""
import asyncio, base64, io, json, math, sys
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image

DIRS = {"front":0.0, "right":math.pi/2, "back":math.pi, "left":3*math.pi/2}
CELL = 128

async def main(glb_path, anim_name, frames, out_dir):
    cyc = json.loads(Path(str(glb_path).rsplit(".",1)[0] + ".cycle.json").read_text())
    dur = cyc["cycle_frames"] / cyc["fps"]
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    import shutil; shutil.copy(glb_path, "/home/nick/output/anim-still/mesh/view/anim.glb")
    async with async_playwright() as p:
        b=await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        pg=await b.new_page(viewport={"width":300,"height":300})
        await pg.goto("http://127.0.0.1:8790/anim.html")
        await pg.wait_for_function("window.__ready===true", timeout=60000)
        clips={}
        for d,az in DIRS.items():
            ims=[]
            for i in range(frames):
                await pg.evaluate(f"window.__at({dur*i/frames}); window.__view({az})")
                data=await pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
                ims.append(Image.open(io.BytesIO(base64.b64decode(data.split(',')[1]))).convert("RGBA"))
            clips[d]=ims
        await b.close()
    boxes=[im.split()[-1].getbbox() for ims in clips.values() for im in ims if im.split()[-1].getbbox()]
    x0=min(b[0] for b in boxes); y0=min(b[1] for b in boxes)
    x1=max(b[2] for b in boxes); y1=max(b[3] for b in boxes)
    cw=max(1,int(round((x1-x0)*CELL/(y1-y0))))
    sheet=Image.new("RGBA",(cw*frames, CELL*len(DIRS)),(0,0,0,0))
    man={"cell":{"w":cw,"h":CELL},"dirs":list(DIRS),
         "anims":{anim_name:{"rows":{},"frames":frames,"fps":12}}}
    for r,(d,ims) in enumerate(clips.items()):
        man["anims"][anim_name]["rows"][d]=r
        for i,im in enumerate(ims):
            sheet.paste(im.crop((x0,y0,x1,y1)).resize((cw,CELL), Image.LANCZOS),(i*cw, r*CELL))
    sheet.save(out/f"{anim_name}.png"); (out/f"{anim_name}.json").write_text(json.dumps(man,indent=1))
    print(f"cycle {cyc['cycle_frames']}f @ {cyc['fps']}fps = {dur:.2f}s -> {frames} cells, cell {cw}x{CELL}")
    print("wrote", out/f"{anim_name}.png")

asyncio.run(main(sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]))
