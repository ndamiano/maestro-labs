"""Render a rigged glb to a sprite sheet: anims as rows-of-facings, the way anim_sheet packs them."""
import asyncio, json, math, sys, base64
from pathlib import Path
from playwright.async_api import async_playwright
from PIL import Image
import numpy as np

ANIMS = {"walk": 8, "idle": 8, "attack": 8}
DIRS = {"front": 0.0, "right": math.pi/2, "back": math.pi, "left": 3*math.pi/2}
CELL = 128


async def main(out_dir):
    out = Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=angle","--use-angle=swiftshader","--enable-unsafe-swiftshader"])
        pg = await b.new_page(viewport={"width": 300, "height": 300})
        errs=[]; pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto("http://127.0.0.1:8790/sheet.html")
        await pg.wait_for_function("window.__ready===true", timeout=60000)
        clips = {}
        for anim, frames in ANIMS.items():
            for d, az in DIRS.items():
                imgs = []
                for i in range(frames):
                    await pg.evaluate(f"window.__pose('{anim}', {i/frames}); window.__view({az})")
                    data = await pg.evaluate("document.querySelector('canvas').toDataURL('image/png')")
                    imgs.append(Image.open(__import__("io").BytesIO(base64.b64decode(data.split(",")[1]))).convert("RGBA"))
                clips[(anim, d)] = imgs
        print("errors:", errs[:2])
        await b.close()

    # one shared box for every cell, so the character never jumps between frames
    boxes = [im.split()[-1].getbbox() for ims in clips.values() for im in ims if im.split()[-1].getbbox()]
    x0=min(b[0] for b in boxes); y0=min(b[1] for b in boxes)
    x1=max(b[2] for b in boxes); y1=max(b[3] for b in boxes)
    bw, bh = x1-x0, y1-y0
    scale = CELL/bh
    cw = max(1,int(round(bw*scale)))
    rows = [(a,d) for a in ANIMS for d in DIRS]
    sheet = Image.new("RGBA", (cw*max(ANIMS.values()), CELL*len(rows)), (0,0,0,0))
    manifest = {"cell": {"w": cw, "h": CELL}, "dirs": list(DIRS), "anims": {}}
    for r,(a,d) in enumerate(rows):
        manifest["anims"].setdefault(a, {"rows": {}, "frames": ANIMS[a], "fps": 12})["rows"][d] = r
        for i,im in enumerate(clips[(a,d)]):
            cell = im.crop((x0,y0,x1,y1)).resize((cw,CELL), Image.LANCZOS)
            sheet.paste(cell, (i*cw, r*CELL))
    sheet.save(out/"aldric_3d.png")
    (out/"aldric_3d.json").write_text(json.dumps(manifest, indent=1))
    print("wrote", out/"aldric_3d.png", sheet.size, "cell", cw, "x", CELL)

asyncio.run(main(sys.argv[1]))
