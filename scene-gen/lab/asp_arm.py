"""Arm 2: LLM extracts relations (never coordinates); clingo solves the layout.

Encoding follows Smith & Mateas (TCIAIG 2011): choice rule assigns one terrain
per cell, integrity constraints carve the design space (bands, coverage,
2x2-block openness, walkable share, anchor-based reachability), items are
placed by the solver under near/cluster/reachable constraints. Solved at 12x16,
upscaled x2 through the same smoothing/render path as arm 1.
"""
import json
import random
import time

import clingo

from .llm import chat_json, TranscriptLogger
from .pipeline import (stage_tileset, stage_objects, upscale_and_smooth,
                       compute_checks, H, W)
from .render import parse_color

CH, CW = 12, 16  # coarse solver grid; x2 -> 24x32


# ---------- LLM relations stage ----------

RELATIONS_SKELETON = """{
  "bands": [
    {"terrain": "W", "side": "south", "depth": 3}
  ],
  "coverage": [
    {"terrain": "G", "min_pct": 40, "max_pct": 80},
    {"terrain": "W", "min_pct": 10, "max_pct": 30}
  ],
  "item_rules": [
    {"symbol": "b", "near": "W", "cluster": false},
    {"symbol": "s", "near": "any", "cluster": true}
  ]
}"""


def stage_relations(place, terrain, items, logger, seed):
    tsyms = [t["symbol"] for t in terrain]
    isyms = [d["symbol"] for d in items]
    legend = ", ".join(f"{t['symbol']}={t['name']}" for t in terrain)
    item_legend = ", ".join(f"{d['symbol']}={d['name']}" for d in items)

    def band_region(b):
        d = b["depth"]
        return {(r, c) for r in range(CH) for c in range(CW)
                if {"north": r < d, "south": r >= CH - d,
                    "west": c < d, "east": c >= CW - d}[b["side"]]}

    def validate(obj):
        for b in obj.get("bands", []):
            if b.get("terrain") not in tsyms:
                return f"band terrain must be one of {tsyms}"
            if b.get("side") not in ("north", "south", "east", "west"):
                return 'band side must be "north", "south", "east" or "west"'
            if not isinstance(b.get("depth"), int) or not (1 <= b["depth"] <= 4):
                return "band depth must be an integer from 1 to 4"
        bands = obj.get("bands", [])
        for i in range(len(bands)):
            for j in range(i + 1, len(bands)):
                a, b = bands[i], bands[j]
                if a["terrain"] != b["terrain"] and band_region(a) & band_region(b):
                    return (f"the {a['terrain']} band on the {a['side']} and the "
                            f"{b['terrain']} band on the {b['side']} claim some of the same "
                            "cells; use bands that occupy different edges (a beach strip "
                            "above a coast is expressed through coverage, not a second band)")
        cov = obj.get("coverage")
        if not isinstance(cov, list) or not cov:
            return "coverage must be a non-empty list"
        for c in cov:
            if c.get("terrain") not in tsyms:
                return f"coverage terrain must be one of {tsyms}"
            lo, hi = c.get("min_pct"), c.get("max_pct")
            if not (isinstance(lo, int) and isinstance(hi, int) and 0 <= lo <= hi <= 100):
                return "min_pct and max_pct must be integers with 0 <= min_pct <= max_pct <= 100"
        if sum(c["min_pct"] for c in cov) > 95:
            return "the min_pct values add up to more than 95; leave the solver some slack"
        rules = obj.get("item_rules")
        if not isinstance(rules, list):
            return "reply needs an item_rules list"
        ruled = {r.get("symbol") for r in rules}
        if ruled != set(isyms):
            return f"item_rules must cover exactly these symbols: {isyms}"
        for r in rules:
            if r.get("near") not in tsyms + ["any"]:
                return f'near must be a terrain symbol from {tsyms} or "any"'
            if not isinstance(r.get("cluster"), bool):
                return "cluster must be true or false"
        return None

    prompt = f"""We are building a 2D tile map of this place: "{place}".
Terrain legend: {legend}
Items to place: {item_legend}

Your job is to describe the map as spatial RELATIONS. A constraint solver will pick the actual tile positions, so you state what must hold, never coordinates.

Reply with only a JSON object in exactly this shape:
{RELATIONS_SKELETON}

Field meanings:
- "bands": terrain strips pinned to a map edge ("a south coast" means a water band on the south side). "depth" is the strip thickness, 1 to 4. Use bands only for edges the place description names; an empty list is valid.
- "coverage": share of the map each terrain gets, as min/max percent. Cover every terrain you want present; a terrain left out may not appear at all. Keep the min_pct sum at 95 or less.
- "item_rules": one entry per item symbol. "near" names a terrain the item must sit within 2 tiles of ("any" means anywhere on its preferred terrain). "cluster": true makes all copies of that item sit close together (a market), false lets them spread (scattered trees)."""
    return chat_json([{"role": "user", "content": prompt}], logger, "relations", seed=seed, validator=validate)


# ---------- ASP encoding ----------

def build_program(terrain, items, relations, min_walk_pct=60, openness=True, coverage=True):
    tidx = {t["symbol"]: i for i, t in enumerate(terrain)}
    iidx = {d["symbol"]: i for i, d in enumerate(items)}
    lines = [
        f"#const rows={CH}.", f"#const cols={CW}.",
        "row(0..rows-1). col(0..cols-1).",
        f"terrain(0..{len(terrain)-1}).",
        "1 { cell(R,C,T) : terrain(T) } 1 :- row(R), col(C).",
        "adj(R,C,R+1,C) :- row(R), col(C), row(R+1).",
        "adj(R,C,R-1,C) :- row(R), col(C), row(R-1).",
        "adj(R,C,R,C+1) :- row(R), col(C), col(C+1).",
        "adj(R,C,R,C-1) :- row(R), col(C), col(C-1).",
    ]
    for t in terrain:
        if t["walkable"]:
            lines.append(f"walk({tidx[t['symbol']]}).")
    lines.append("walkcell(R,C) :- cell(R,C,T), walk(T).")

    # bands
    band_cells = set()
    for b in relations.get("bands", []):
        ti, d = tidx[b["terrain"]], b["depth"]
        cond = {"north": f"R < {d}", "south": f"R >= rows-{d}",
                "west": f"C < {d}", "east": f"C >= cols-{d}"}[b["side"]]
        lines.append(f":- row(R), col(C), {cond}, not cell(R,C,{ti}).")
        for r in range(CH):
            for c in range(CW):
                ok = {"north": r < d, "south": r >= CH - d,
                      "west": c < d, "east": c >= CW - d}[b["side"]]
                if ok:
                    band_cells.add((r, c))

    total = CH * CW
    if coverage:
        for cvg in relations.get("coverage", []):
            ti = tidx[cvg["terrain"]]
            lo = cvg["min_pct"] * total // 100
            hi = max(cvg["max_pct"] * total // 100, lo)
            if lo > 0:
                lines.append(f":- #count{{ R,C : cell(R,C,{ti}) }} < {lo}.")
            lines.append(f":- #count{{ R,C : cell(R,C,{ti}) }} > {hi}.")

    # walkable share of open ground (cells outside named bands)
    open_cells = total - len(band_cells)
    min_walk = min_walk_pct * open_cells // 100
    lines.append(f":- #count{{ R,C : walkcell(R,C) }} < {min_walk}.")

    if openness:
        # every cell must belong to a 2x2 block of its own terrain: patches, not corridors
        lines += [
            "sq(R,C,T) :- cell(R,C,T), cell(R,C+1,T), cell(R+1,C,T), cell(R+1,C+1,T).",
            "inblock(R,C,T) :- sq(R,C,T).",
            "inblock(R,C+1,T) :- sq(R,C,T).",
            "inblock(R+1,C,T) :- sq(R,C,T).",
            "inblock(R+1,C+1,T) :- sq(R,C,T).",
            ":- cell(R,C,T), not inblock(R,C,T).",
        ]

    # connectivity: one anchor, closure, every walkable cell reached
    lines += [
        "1 { anchor(R,C) : row(R), col(C) } 1.",
        ":- anchor(R,C), not walkcell(R,C).",
        "reach(R,C) :- anchor(R,C).",
        "reach(R2,C2) :- reach(R,C), adj(R,C,R2,C2), walkcell(R2,C2).",
        ":- walkcell(R,C), not reach(R,C).",
    ]

    # items
    rules = {r["symbol"]: r for r in relations["item_rules"]}
    lines.append("nearok(R,C,T) :- row(R), col(C), cell(R2,C2,T), |R-R2|+|C-C2| <= 2.")
    lines.append("reachnear(R,C) :- row(R), col(C), reach(R2,C2), |R-R2|+|C-C2| <= 1.")
    for d in items:
        ii, ti = iidx[d["symbol"]], tidx[d["on_terrain"]]
        r = rules[d["symbol"]]
        lines.append(f"itemcopy({ii},1..{d['count']}).")
        lines.append(f"pref({ii},{ti}).")
        if r["near"] != "any":
            lines.append(f"near({ii},{tidx[r['near']]}).")
        if r["cluster"] and d["count"] > 1:
            lines.append(f"cluster({ii}).")
    lines += [
        "1 { at(I,K,R,C) : row(R), col(C) } 1 :- itemcopy(I,K).",
        ":- at(I,K,R,C), pref(I,T), not cell(R,C,T).",
        ":- row(R), col(C), #count{ I,K : at(I,K,R,C) } > 1.",
        ":- at(I,K,R,C), near(I,T), not nearok(R,C,T).",
        ":- at(I,K,R,C), not reachnear(R,C).",
        ":- cluster(I), at(I,K1,R1,C1), at(I,K2,R2,C2), |R1-R2| > 3.",
        ":- cluster(I), at(I,K1,R1,C1), at(I,K2,R2,C2), |C1-C2| > 3.",
        "#show cell/3.",
        "#show at/4.",
    ]
    return "\n".join(lines)


def solve(program, seed, timeout=90):
    ctl = clingo.Control(["--seed", str(seed), "--sign-def=rnd", "--rand-freq=0.7",
                          "--restart-on-model", "1"])
    ctl.add("base", [], program)
    ctl.ground([("base", [])])
    model_atoms = []

    def on_model(m):
        model_atoms.clear()
        model_atoms.extend(m.symbols(shown=True))

    with ctl.solve(on_model=on_model, async_=True) as handle:
        finished = handle.wait(timeout)
        if not finished:
            handle.cancel()
        result = handle.get()
    if not model_atoms:
        return None, str(result)
    return model_atoms, str(result)


def decode(atoms, terrain, items):
    tsym = {i: t["symbol"] for i, t in enumerate(terrain)}
    isym = {i: d["symbol"] for i, d in enumerate(items)}
    grid = [[None] * CW for _ in range(CH)]
    placements = []
    for a in atoms:
        if a.name == "cell":
            r, c, t = (x.number for x in a.arguments)
            grid[r][c] = tsym[t]
        elif a.name == "at":
            i, _k, r, c = (x.number for x in a.arguments)
            placements.append({"symbol": isym[i], "row": r, "col": c})
    return ["".join(row) for row in grid], placements


# ---------- driver ----------

def refine_placements(placements, coarse_grid, fine_grid, items, rng):
    """Map coarse (r,c) to a fine cell inside the 2x2 block, preferring right terrain."""
    pref = {d["symbol"]: d["on_terrain"] for d in items}
    taken = set()
    out = []
    for p in placements:
        opts = [(p["row"] * 2 + dr, p["col"] * 2 + dc) for dr in (0, 1) for dc in (0, 1)]
        rng.shuffle(opts)
        opts.sort(key=lambda rc: fine_grid[rc[0]][rc[1]] != pref[p["symbol"]])
        for r, c in opts:
            if (r, c) not in taken:
                taken.add((r, c))
                out.append({"symbol": p["symbol"], "row": r, "col": c})
                break
    return out


def generate_map_asp(place, seed, out_prefix):
    rng = random.Random(seed)
    logger = TranscriptLogger(f"{out_prefix}_transcript.jsonl")
    t0 = time.time()

    tileset = stage_tileset(place, logger, seed)
    terrain = tileset["terrain"]
    for i, t in enumerate(terrain):
        t["color"] = parse_color(t.get("color"), i)
    obj_spec = stage_objects(place, terrain, logger, seed)
    items = obj_spec["objects"] + obj_spec["entities"]
    relations = stage_relations(place, terrain, items, logger, seed)
    llm_seconds = round(time.time() - t0, 1)

    t1 = time.time()
    ladder = [
        {"openness": True, "coverage": True, "label": "full"},
        {"openness": False, "coverage": True, "label": "no_openness"},
        {"openness": False, "coverage": False, "label": "no_openness_no_coverage"},
        {"openness": False, "coverage": False, "label": "no_bands", "drop_bands": True},
    ]
    atoms = None
    solve_log = []
    for level in ladder:
        rel = dict(relations, bands=[]) if level.get("drop_bands") else relations
        program = build_program(terrain, items, rel,
                                openness=level["openness"], coverage=level["coverage"])
        atoms, status = solve(program, seed)
        solve_log.append({"level": level["label"], "status": status,
                          "seconds": round(time.time() - t1, 1)})
        if atoms:
            break
    if not atoms:
        raise RuntimeError(f"UNSAT at every relaxation level: {solve_log}")
    solve_seconds = round(time.time() - t1, 1)

    coarse_grid, coarse_placements = decode(atoms, terrain, items)
    walkable_syms = {t["symbol"] for t in terrain if t["walkable"]}
    grid = upscale_and_smooth(coarse_grid, walkable_syms, rng, scale=2)
    placements = refine_placements(coarse_placements, coarse_grid, grid, items, rng)

    checks = compute_checks(grid, terrain, placements, items)
    result = {
        "arm": "asp",
        "place": place,
        "seed": seed,
        "terrain": terrain,
        "items": items,
        "relations": relations,
        "grid": grid,
        "placements": placements,
        "solve_log": solve_log,
        "history": [{"stage": "solved", "checks": checks}],
        "cost": {
            "calls": logger.calls,
            "prompt_tokens": logger.prompt_tokens,
            "completion_tokens": logger.completion_tokens,
            "llm_seconds": llm_seconds,
            "solve_seconds": solve_seconds,
            "wall_seconds": round(time.time() - t0, 1),
        },
    }
    with open(f"{out_prefix}_map.json", "w") as f:
        json.dump(result, f, indent=1)
    return result
