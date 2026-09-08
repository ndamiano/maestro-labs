"""Run the Word2World-recipe study: 4 places x 3 seeds on the local 27B."""
import argparse
import json
import os
import traceback

from lab.pipeline import generate_map
from lab.render import render_map, contact_sheet, parse_color

PLACES = {
    "fishing_village": "a fishing village on a south coast",
    "dungeon_floor": "a dungeon floor with a locked treasury",
    "forest_clearing": "a forest clearing with a hermit hut",
    "desert_oasis": "a desert oasis market",
}
SEEDS = [1, 2, 3]
OUT = "output"


def render_result(result, out_prefix):
    terrain_colors = {t["symbol"]: t["color"] for t in result["terrain"]}
    object_colors = {}
    for i, d in enumerate(result["items"]):
        object_colors[d["symbol"]] = parse_color(d.get("color"), i + 7)
    render_map(result["grid"], terrain_colors, result["placements"], object_colors,
               f"{out_prefix}_map.png")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--places", nargs="*", default=list(PLACES))
    ap.add_argument("--seeds", nargs="*", type=int, default=SEEDS)
    args = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    summary = []
    for key in args.places:
        place = PLACES[key]
        pdir = os.path.join(OUT, key)
        os.makedirs(pdir, exist_ok=True)
        seed_pngs, seed_labels = [], []
        for seed in args.seeds:
            prefix = os.path.join(pdir, f"seed{seed}")
            print(f"=== {key} seed {seed} ===", flush=True)
            try:
                result = generate_map(place, seed, prefix)
                render_result(result, prefix)
                seed_pngs.append(f"{prefix}_map.png")
                final = result["history"][-1]["checks"]
                seed_labels.append(
                    f"seed {seed} | walk {final['walkable_frac']:.0%} "
                    f"conn {final['largest_component_frac']:.0%} | "
                    f"{result['cost']['calls']} calls {result['cost']['wall_seconds']}s")
                summary.append({"place": key, "seed": seed, "ok": True,
                                "checks": final, "cost": result["cost"],
                                "history": result["history"],
                                "snapped": result["snapped_placements"]})
                print(f"    ok: {seed_labels[-1]}", flush=True)
            except Exception as e:
                traceback.print_exc()
                summary.append({"place": key, "seed": seed, "ok": False, "error": str(e)})
        if seed_pngs:
            contact_sheet(seed_pngs, seed_labels,
                          os.path.join(OUT, f"sheet_{key}.png"), title=place)
    with open(os.path.join(OUT, "summary.json"), "w") as f:
        json.dump(summary, f, indent=1)
    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main()
