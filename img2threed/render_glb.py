"""Textured GLB → 3-view sheet via three.js in headless chromium.

    python render_glb.py <out.png> <file.glb>
"""
import os, shutil, socket, subprocess, sys, time
from playwright.sync_api import sync_playwright
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
VIEW = os.path.join(HERE, "glbview")
VENDOR = "/home/nick/Documents/ai-agent-test/runtime/vendor"
for f in ("three.module.js", "GLTFLoader.js", "BufferGeometryUtils.js"):
    if not os.path.exists(os.path.join(VIEW, f)):
        shutil.copy(os.path.join(VENDOR, f), VIEW)
out, glb = sys.argv[1], os.path.abspath(sys.argv[2])
os.makedirs(os.path.join(VIEW, "m"), exist_ok=True)
link = os.path.join(VIEW, "m", os.path.basename(glb))
if os.path.lexists(link):
    os.remove(link)
os.symlink(glb, link)

s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1"], cwd=VIEW,
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
VIEWS = [(35, 20), (125, 10), (215, 25)]
try:
    with sync_playwright() as p:
        b = p.chromium.launch(args=["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"])
        pg = b.new_page(viewport={"width": 512, "height": 512})
        tiles = []
        for i, (az, el) in enumerate(VIEWS):
            pg.goto(f"http://127.0.0.1:{port}/index.html?glb=m/{os.path.basename(glb)}&az={az}&el={el}&size=512&nometal={os.environ.get("NOMETAL","")}")
            pg.wait_for_function("window.__ready===true", timeout=120000)
            err = pg.evaluate("window.__err")
            if err:
                sys.exit(f"load error: {err}")
            pg.wait_for_timeout(500)
            path = f"{out}.{i}.png"; pg.screenshot(path=path); tiles.append(path)
        b.close()
finally:
    srv.terminate()
sheet = Image.new("RGB", (1536, 512), "white")
for i, t in enumerate(tiles):
    sheet.paste(Image.open(t), (i * 512, 0)); os.remove(t)
sheet.save(out); print(out)
