"""Arm 2 sweep: same 4 places x 3 seeds, ASP layout. Rebuild combined contact sheets."""
import argparse
import json
import os
import traceback

from lab.asp_arm import generate_map_asp
from lab.render import contact_sheet
from run_experiment import PLACES, SEEDS, OUT, render_result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--places", nargs="*", default=list(PLACES))
    ap.add_argument("--seeds", nargs="*", type=int, default=SEEDS)
    args = ap.parse_args()

    summary = []
    for key in args.places:
        place = PLACES[key]
        pdir = os.path.join(OUT, key)
        os.makedirs(pdir, exist_ok=True)
        for seed in args.seeds:
            prefix = os.path.join(pdir, f"asp_seed{seed}")
            print(f"=== ASP {key} seed {seed} ===", flush=True)
            try:
                result = generate_map_asp(place, seed, prefix)
                render_result(result, prefix)
                summary.append({"place": key, "seed": seed, "ok": True,
                                "checks": result["history"][-1]["checks"],
                                "cost": result["cost"],
                                "solve_log": result["solve_log"]})
                print(f"    ok: {summary[-1]['checks']} {result['cost']}", flush=True)
            except Exception as e:
                traceback.print_exc()
                summary.append({"place": key, "seed": seed, "ok": False, "error": str(e)})
        # combined sheet: arm1 seeds then arm2 seeds
        pngs, labels = [], []
        for seed in SEEDS:
            p = os.path.join(pdir, f"seed{seed}_map.png")
            if os.path.exists(p):
                pngs.append(p)
                labels.append(f"arm1 LLM | seed {seed}")
        for seed in args.seeds:
            p = os.path.join(pdir, f"asp_seed{seed}_map.png")
            if os.path.exists(p):
                pngs.append(p)
                labels.append(f"arm2 ASP | seed {seed}")
        if pngs:
            contact_sheet(pngs, labels, os.path.join(OUT, f"sheet_{key}.png"), title=place)
    with open(os.path.join(OUT, "summary_arm2.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
