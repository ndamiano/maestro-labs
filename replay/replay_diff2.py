from pathlib import Path
import replay
import sys, difflib
r = replay.run_to_position(Path(sys.argv[1]), 999, Path(sys.argv[2]))
for t in r.diverged:
    for ln in [l.strip() for l in t.replayed.splitlines() if l.strip()]:
        if ln in t.recorded: continue
        near = difflib.get_close_matches(ln, [l.strip() for l in t.recorded.splitlines()], 1, 0.5)
        if not near:
            print(f"turn {t.turn}: line absent entirely:", ln[:200]); break
        a, b = ln, near[0]
        i = next((k for k in range(min(len(a),len(b))) if a[k]!=b[k]), min(len(a),len(b)))
        print(f"turn {t.turn}: diverges at char {i} of {len(a)}")
        print("  replayed:", a[max(0,i-90):i+90])
        print("  recorded:", b[max(0,i-90):i+90])
        break
