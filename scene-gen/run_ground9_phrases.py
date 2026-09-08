"""Phase 1: the layout LLM authors each terrain's paint phrase and guide color.

Needs ninfer on :8090. Output: output/<place>/seed<N>_paintspec.json
"""
import json
import sys
from pathlib import Path

from lab.llm import chat, TranscriptLogger

MAPS = [("fishing_village", 2), ("desert_oasis", 2), ("forest_clearing", 1), ("dungeon_floor", 3)]

SKELETON = """{
  "terrains": [
    {"name": "<terrain name from the list>",
     "color": "<hex like #8a9b6c — the flat color this region is painted before texturing>",
     "phrase": "<5-12 words describing ONLY the ground material seen from directly above>"}
  ]
}"""


def spec_for(place_request, terrain_names, logger):
    system = (
        "You art-direct top-down 2d game terrain. For each terrain region you write the flat "
        "base color and a short material phrase for an image model. Rules that matter:\n"
        "- color: muted, natural, painterly. Desaturated earth tones unless the material IS "
        "vivid (gold coins, lava). Never neon, never pure primaries.\n"
        "- phrase: the ground material only — no objects, no buildings, no creatures, "
        "no story. Say what the surface is made of and how it reads from above.\n"
        "Answer with JSON exactly in this shape:\n" + SKELETON)
    user = (f"The place: {place_request}\n"
            f"The terrain regions: {', '.join(terrain_names)}\n"
            "Write color and phrase for every region.")
    for attempt in range(3):
        text = chat([{"role": "system", "system": system, "content": system},
                     {"role": "user", "content": user}],
                    logger, "paintspec", temperature=0.4)
        try:
            data = json.loads(text[text.index("{"):text.rindex("}") + 1])
            byname = {t["name"]: t for t in data["terrains"]}
            missing = [n for n in terrain_names if n not in byname]
            if not missing:
                return byname
            user += f"\nYour last answer missed: {', '.join(missing)}. Answer again, complete."
        except (ValueError, KeyError, TypeError) as e:
            user += f"\nYour last answer was not valid JSON in the required shape ({e}). Again."
    raise SystemExit(f"no valid spec after 3 attempts for {place_request}")


REQUESTS = {
    "fishing_village": "a fishing village on a south coast",
    "desert_oasis": "a desert oasis market",
    "forest_clearing": "a forest clearing with a hermit hut",
    "dungeon_floor": "a dungeon floor with a locked treasury",
}


def main():
    for place, seed in MAPS:
        m = json.load(open(f"output/{place}/seed{seed}_map.json"))
        names = [t["name"] for t in m["terrain"]]
        logger = TranscriptLogger(f"output/{place}/seed{seed}_paintspec_transcript.jsonl")
        spec = spec_for(REQUESTS[place], names, logger)
        out = Path(f"output/{place}/seed{seed}_paintspec.json")
        out.write_text(json.dumps(spec, indent=2))
        print(place, "->", {n: (s["color"], s["phrase"]) for n, s in spec.items()})


if __name__ == "__main__":
    sys.exit(main())
