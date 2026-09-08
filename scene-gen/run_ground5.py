"""Round 5: blend pass — low-denoise global img2img over the regional result.

Regional pass nails per-region material; this pass harmonizes lighting and
softens region seams. Sweep 0.25/0.35/0.45.
"""
import json
from pathlib import Path

from PIL import Image, ImageDraw

from run_ground import guide_image, terrain_prompt, upload, workflow, run_wf, MAPS

DENOISES = [0.25, 0.35, 0.45]


def main():
    outdir = Path("output/ground5")
    outdir.mkdir(parents=True, exist_ok=True)
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        prompt = terrain_prompt(m) + ", unified soft lighting, seamless natural transitions"
        regional = Image.open(f"output/ground4/{place}_regional_dn55.png")
        up = f"lab_g5_{place}_{seed}.png"
        upload(regional, up)
        results, labels = [regional], ["regional (in)"]
        for dn in DENOISES:
            img = run_wf(workflow(up, prompt, dn, seed=7))
            img.save(outdir / f"{place}_blend_dn{int(dn * 100)}.png")
            results.append(img)
            labels.append(f"blend {dn}")
        w, h = results[0].width // 2, results[0].height // 2
        pad = 6
        sheet = Image.new("RGB", (pad + len(results) * (w + pad), h + 36), "#222222")
        d = ImageDraw.Draw(sheet)
        d.text((pad, 3), f"{place} — blend pass over regional", fill="#ffffff")
        for i, (im, lab) in enumerate(zip(results, labels)):
            x = pad + i * (w + pad)
            sheet.paste(im.resize((w, h)), (x, 18))
            d.text((x, h + 21), lab, fill="#ffffff")
        sheet.save(outdir / f"sheet_{place}.png")
        print(place, "done")


if __name__ == "__main__":
    main()
