"""Content-based facing picker for a turntable clip.

The physical cue, not the clock: a PROFILE is asymmetric about the vertical axis and a
FRONT or BACK view is not. So the turn's two asymmetry peaks are the profiles, and the
symmetry trough between them is the back. Which profile is which follows from the order
the clip turns in (screen-right first), and the pair is checked by mirroring: a right
profile mirrored is a left profile.
"""
import sys
import numpy as np
from PIL import Image

sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from worker import anim_sheet as sheets  # noqa


def _sil(im, size=192):
    a = sheets.matte(im.convert("RGB"))
    box = a.split()[-1].getbbox()
    a = a.crop(box).resize((size, size), Image.BILINEAR)
    return np.asarray(a.split()[-1], dtype=float) / 255.0


def pick(frames):
    """{front, right, back, left} as frame indices.

    The pair first: a right profile MIRRORED is a left profile, and no other two frames of a
    turn are each other's reflection. Both are asymmetric — that is what makes them profiles —
    and the back is the symmetric frame that lies between them.
    """
    S = [_sil(f) for f in frames]
    n = len(S)
    asym = np.array([np.abs(s - s[:, ::-1]).mean() for s in S])
    moving = np.flatnonzero(sheets.motion_signal(frames) > sheets.STILL_DIFF)
    lo = max(1, int(moving[0])) if len(moving) else 1
    hi = int(moving[-1]) if len(moving) else n - 1
    cand = [i for i in range(lo, hi + 1) if asym[i] >= np.median(asym[lo:hi + 1])]

    best = (1e9, None, None)
    for a in range(len(cand)):
        for b in range(a + 1, len(cand)):
            i, j = cand[a], cand[b]
            if j - i < 3:
                continue
            # mirrored profiles agree; the pair is also rewarded for being strongly profiled,
            # so two near-front frames cannot win by being bland
            residual = np.abs(S[i][:, ::-1] - S[j]).mean() - 0.25 * min(asym[i], asym[j])
            if residual < best[0]:
                best = (residual, i, j)
    _, right, left = best
    if right is None:
        right, left = lo, hi
    mid = np.arange(right + 1, left)
    back = int(mid[np.argmin(asym[mid])]) if len(mid) else right
    mirror = float(np.abs(S[right][:, ::-1] - S[left]).mean())
    return {"front": 0, "right": right, "back": back, "left": left}, mirror


if __name__ == "__main__":
    import glob, os, re, time
    from PIL import ImageDraw
    fs = sorted(glob.glob("/home/nick/comfy/mess-with-comfy/output/anim_*.png"),
                key=lambda p: int(re.search(r"anim_(\d+)_", p).group(1)))
    recent = [f for f in fs if os.path.getmtime(f) > time.time() - 5 * 3600]
    turn = [Image.open(c).convert("RGB") for c in recent[374:396]]
    new, mirror = pick(turn)
    old = sheets.pick_facings(turn)
    print("quarter-mark (today):", old)
    print("asymmetry    (new)  :", new, f"  mirror residual {mirror:.4f}")
    out = "/home/nick/output/anim-still/facings"
    os.makedirs(out, exist_ok=True)
    for name, p in (("old_quarter_marks", old), ("new_asymmetry", new)):
        sheet = Image.new("RGB", (256 * 4, 288), (18, 18, 22))
        dr = ImageDraw.Draw(sheet)
        for k, d in enumerate(("front", "right", "back", "left")):
            sheet.paste(turn[p[d]].resize((256, 256)), (256 * k, 32))
            dr.text((256 * k + 8, 10), f"{d}   frame {p[d]}", fill=(232, 232, 238))
        sheet.save(f"{out}/{name}.png")
    print("wrote", out)
