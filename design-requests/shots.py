"""Two in-game screenshots per build: after start, and after ~6s of input. usage: shots.py <slug:run> ..."""
import sys, functools, http.server, threading
from pathlib import Path
from playwright.sync_api import sync_playwright
RUNS = Path('/home/nick/output/runs'); OUT = Path(__file__).parent / 'shots'; OUT.mkdir(exist_ok=True)
for arg in sys.argv[1:]:
    slug, rid = arg.split(':'); g = RUNS / rid / 'game'
    H = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(g))
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
    errs = []
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader']); p = b.new_page(viewport={'width':1280,'height':720})
        p.on('pageerror', lambda e: errs.append(str(e)))
        p.goto(f'http://127.0.0.1:{srv.server_address[1]}/index.html', timeout=20000); p.wait_for_timeout(2500)
        p.screenshot(path=str(OUT/f'{slug}.0title.png'))
        p.mouse.click(640,450); p.wait_for_timeout(300); p.keyboard.press('Enter'); p.keyboard.press('Space'); p.wait_for_timeout(1500)
        p.screenshot(path=str(OUT/f'{slug}.1start.png'))
        for k in ['KeyD','KeyD','Space','KeyW','KeyD','KeyE','Space','KeyA','KeyJ','KeyF','KeyK','KeyD','Space']:
            p.keyboard.down(k); p.wait_for_timeout(350); p.keyboard.up(k); p.wait_for_timeout(150)
        p.mouse.click(300,600); p.wait_for_timeout(500); p.mouse.click(640,300); p.wait_for_timeout(1500)
        p.screenshot(path=str(OUT/f'{slug}.2play.png')); b.close()
    srv.shutdown(); print(slug, 'errors:', errs)
