"""10 new places, one seed each: layout + paintspec (LLM phase)."""
import json
import os

from lab.pipeline import generate_map
from lab.llm import chat, TranscriptLogger
from run_experiment import render_result
from run_ground9_phrases import SKELETON

PLACES = {
    "volcano_forge": "a blacksmith forge on the slope of a volcano",
    "snow_village": "a snowy mountain village around a frozen lake",
    "witch_bog": "a murky swamp with a witch's hut on stilts",
    "castle_courtyard": "a stone castle courtyard with a fountain and stables",
    "graveyard": "an overgrown graveyard with a small chapel",
    "jungle_ruins": "ancient jungle temple ruins with a broken staircase",
    "farm": "a tidy farm with fields, a barn and a duck pond",
    "port_market": "a busy port town market along a stone quay",
    "ice_cave": "an ice cave with a frozen underground river",
    "canyon_outpost": "a desert canyon outpost beside a dry riverbed",
}
SEED = 1


def paintspec(place_request, terrains, logger):
    system = (
        "You art-direct top-down 2d game terrain. For each terrain region you write the flat "
        "base color and a short material phrase for an image model. Rules:\n"
        "- color: muted, natural, painterly. Desaturated earth tones unless the material IS "
        "vivid (gold coins, lava, glowing crystal — those stay saturated). Never neon.\n"
        "- The layout designer already chose a rough color per region; treat it as the "
        "region's INTENT and refine it into a painterly hex, keeping vivid identity colors "
        "vivid.\n"
        "- phrase: the ground material only — no objects, no buildings, no creatures.\n"
        "Answer with JSON exactly in this shape:\n" + SKELETON)
    user = (f"The place: {place_request}\n"
            "The terrain regions (name, designer's rough color):\n"
            + "\n".join(f"- {n}: {c}" for n, c in terrains)
            + "\nWrite color and phrase for every region.")
    names = [n for n, _ in terrains]
    for attempt in range(3):
        text = chat([{"role": "system", "content": system},
                     {"role": "user", "content": user}], logger, "paintspec", temperature=0.4)
        try:
            data = json.loads(text[text.index("{"):text.rindex("}") + 1])
            byname = {t["name"]: t for t in data["terrains"]}
            if not [n for n in names if n not in byname]:
                return byname
        except (ValueError, KeyError, TypeError):
            pass
        user += "\nIncomplete or invalid. Answer again, all regions, exact JSON shape."
    raise RuntimeError(f"no paintspec for {place_request}")


def main():
    for key, request in PLACES.items():
        pdir = os.path.join("output", key)
        os.makedirs(pdir, exist_ok=True)
        prefix = os.path.join(pdir, f"seed{SEED}")
        print(f"=== {key} ===", flush=True)
        result = generate_map(request, SEED, prefix)
        render_result(result, prefix)
        logger = TranscriptLogger(f"{prefix}_paintspec_transcript.jsonl")
        terrains = [(t["name"], t["color"]) for t in result["terrain"]]
        spec = paintspec(request, terrains, logger)
        json.dump(spec, open(f"{prefix}_paintspec.json", "w"), indent=2)
        print(f"    map + spec ok ({result['cost']['calls']} calls)", flush=True)


if __name__ == "__main__":
    main()
