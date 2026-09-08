"""Word2World-style pipeline decomposed into small focused calls for a 27B model.

Stages per map:
  1. terrain tileset (JSON)
  2. objects + entities (JSON)
  3. coarse terrain zone grid 6x8 -> deterministic x4 upscale + majority smoothing -> 24x32
  4. fine pass: line/rect paint ops for paths, rivers, walls
  5. placement: entity/object coordinates
  6. self-critique rounds: critique (issues) -> fix (ops + moves)
Programmatic checks after each stage that changes the map.
"""
import copy
import json
import random
import time

from .llm import chat_json, TranscriptLogger
from .checks import walkable_stats
from .render import parse_color

COARSE_H, COARSE_W = 6, 8
SCALE = 4
H, W = COARSE_H * SCALE, COARSE_W * SCALE  # 24 x 32


# ---------- stage 1: terrain tileset ----------

TILESET_SKELETON = """{
  "terrain": [
    {"symbol": "G", "name": "grass", "walkable": true, "color": "#4caf50"},
    {"symbol": "W", "name": "water", "walkable": false, "color": "#2196f3"}
  ]
}"""


def stage_tileset(place, logger, seed):
    def validate(obj):
        t = obj.get("terrain")
        if not isinstance(t, list) or not (3 <= len(t) <= 8):
            return "terrain must be a list of 3 to 8 tiles"
        syms = [d.get("symbol", "") for d in t]
        if any(not (isinstance(s, str) and len(s) == 1 and s.isalpha() and s.isupper()) for s in syms):
            return "every symbol must be a single uppercase letter"
        if len(set(syms)) != len(syms):
            return "symbols must be unique"
        if any(not isinstance(d.get("walkable"), bool) for d in t):
            return "every tile needs walkable true or false"
        if not any(d["walkable"] for d in t):
            return "at least one terrain must be walkable"
        return None

    prompt = f"""We are building a 2D tile map of this place: "{place}".

First step: decide the terrain tile classes (ground, water, floors, walls — the base layer only; objects and characters come later).

Reply with only a JSON object in exactly this shape:
{TILESET_SKELETON}

Field meanings:
- "symbol": single uppercase letter, unique per tile.
- "name": short terrain name.
- "walkable": true when a person can stand on it.
- "color": hex color for rendering.

Choose 4 to 7 terrain classes that fit the place. Most of the map should be standable ground, so include at least two walkable terrain types."""
    return chat_json([{"role": "user", "content": prompt}], logger, "tileset", seed=seed, validator=validate)


# ---------- stage 2: objects and entities ----------

OBJECTS_SKELETON = """{
  "objects": [
    {"symbol": "h", "name": "hut", "count": 1, "on_terrain": "G", "walkable": false}
  ],
  "entities": [
    {"symbol": "f", "name": "fisherman", "count": 2, "on_terrain": "G"}
  ]
}"""


def stage_objects(place, terrain, logger, seed):
    terrain_desc = json.dumps([{k: t[k] for k in ("symbol", "name", "walkable")} for t in terrain])
    terrain_syms = {t["symbol"] for t in terrain}

    def validate(obj):
        objs, ents = obj.get("objects"), obj.get("entities")
        if not isinstance(objs, list) or not isinstance(ents, list):
            return "reply needs both an objects list and an entities list"
        seen = set(terrain_syms)
        for d in objs + ents:
            s = d.get("symbol", "")
            if not (isinstance(s, str) and len(s) == 1 and s.islower()):
                return "every object and entity symbol must be a single lowercase letter"
            if s in seen:
                return f"symbol '{s}' is already used; each symbol must be unique"
            seen.add(s)
            if d.get("on_terrain") not in terrain_syms:
                return f"on_terrain for '{d.get('name')}' must be one of the terrain symbols {sorted(terrain_syms)}"
            if not isinstance(d.get("count"), int) or not (1 <= d["count"] <= 8):
                return "count must be an integer from 1 to 8"
        if len(objs) + len(ents) < 2:
            return "include at least 2 items in total"
        if len(objs) + len(ents) > 10:
            return "keep it to at most 10 items in total"
        return None

    prompt = f"""We are building a 2D tile map of this place: "{place}".
The terrain tiles are already decided: {terrain_desc}

Second step: list the objects (buildings, props) and entities (people, animals) that belong in this place.

Reply with only a JSON object in exactly this shape:
{OBJECTS_SKELETON}

Field meanings:
- "symbol": single lowercase letter, unique, different from the terrain symbols.
- "count": how many copies to place (1 to 8).
- "on_terrain": the terrain symbol this item stands on.
- objects also need "walkable": true when a person can step onto that tile (a door, a bridge), false when it blocks (a wall, a hut).

List 2 to 10 items in total. Include the things the place description implies."""
    return chat_json([{"role": "user", "content": prompt}], logger, "objects", seed=seed, validator=validate)


# ---------- stage 3: coarse layout ----------

def stage_coarse(place, terrain, logger, seed):
    syms = [t["symbol"] for t in terrain]
    legend = ", ".join(f"{t['symbol']}={t['name']}" for t in terrain)
    example_row = syms[0] * COARSE_W

    def validate(obj):
        rows = obj.get("rows")
        if not isinstance(rows, list) or len(rows) != COARSE_H:
            return f"rows must be a list of exactly {COARSE_H} strings"
        for r in rows:
            if not isinstance(r, str) or len(r) != COARSE_W:
                return f"every row must be a string of exactly {COARSE_W} letters"
            bad = [ch for ch in r if ch not in syms]
            if bad:
                return f"row contains letters {bad} that are not terrain symbols {syms}"
        used = {ch for r in rows for ch in r}
        if len(used) < 2:
            return "use at least 2 different terrain types across the map"
        return None

    prompt = f"""We are building a 2D tile map of this place: "{place}".
Terrain legend: {legend}

Third step: paint the coarse layout. The map is a grid of {COARSE_H} rows by {COARSE_W} columns. Each cell is one large terrain zone (it will later be blown up to 4x4 tiles), so this grid sets the broad geography: where the water is, where the ground is, where built areas sit.

Reply with only a JSON object in exactly this shape:
{{
  "rows": ["{example_row}", "... {COARSE_H} rows total, each exactly {COARSE_W} letters ..."]
}}

Every letter must be one of: {", ".join(syms)}.
Row 1 is the north edge, the last row is the south edge. Column 1 is west, the last column is east.
Think about what the place description says about geography (a coast means water along one edge, a clearing means open ground surrounded by trees) and paint zones that match it. Large connected regions read better than scattered single cells."""
    return chat_json([{"role": "user", "content": prompt}], logger, "coarse", seed=seed, validator=validate)


def upscale_and_smooth(rows, walkable_syms, rng, scale=SCALE):
    grid = []
    for r in rows:
        row = "".join(ch * scale for ch in r)
        for _ in range(scale):
            grid.append(list(row))
    # majority smoothing to soften block edges, 2 passes
    for _ in range(2):
        new = copy.deepcopy(grid)
        for r in range(H):
            for c in range(W):
                counts = {}
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < H and 0 <= nc < W:
                            counts[grid[nr][nc]] = counts.get(grid[nr][nc], 0) + 1
                best = max(counts.items(), key=lambda kv: (kv[1], kv[0] == grid[r][c]))
                if best[1] >= 6:
                    new[r][c] = best[0]
        grid = new
    return ["".join(r) for r in grid]


# ---------- stage 4: fine pass (paint ops) ----------

OPS_SKELETON = """{
  "ops": [
    {"op": "line", "tile": "P", "from": [2, 3], "to": [18, 3]},
    {"op": "rect", "tile": "W", "top_left": [5, 10], "bottom_right": [9, 20], "fill": false}
  ]
}"""


def _valid_pt(p):
    return (isinstance(p, list) and len(p) == 2 and all(isinstance(x, int) for x in p)
            and 0 <= p[0] < H and 0 <= p[1] < W)


def make_ops_validator(terrain_syms, max_ops=12):
    def validate(obj):
        ops = obj.get("ops")
        if not isinstance(ops, list):
            return "reply needs an ops list"
        if len(ops) > max_ops:
            return f"use at most {max_ops} ops"
        for o in ops:
            if o.get("op") not in ("line", "rect"):
                return "each op must be \"line\" or \"rect\""
            if o.get("tile") not in terrain_syms:
                return f"tile must be one of the terrain symbols {sorted(terrain_syms)}"
            if o["op"] == "line":
                if not (_valid_pt(o.get("from")) and _valid_pt(o.get("to"))):
                    return f"line needs from and to as [row, col] with row 0..{H-1}, col 0..{W-1}"
            else:
                if not (_valid_pt(o.get("top_left")) and _valid_pt(o.get("bottom_right"))):
                    return f"rect needs top_left and bottom_right as [row, col] with row 0..{H-1}, col 0..{W-1}"
        return None
    return validate


def apply_ops(grid, ops):
    g = [list(r) for r in grid]
    for o in ops:
        t = o["tile"]
        if o["op"] == "line":
            (r0, c0), (r1, c1) = o["from"], o["to"]
            steps = max(abs(r1 - r0), abs(c1 - c0), 1)
            for i in range(steps + 1):
                r = round(r0 + (r1 - r0) * i / steps)
                c = round(c0 + (c1 - c0) * i / steps)
                g[r][c] = t
        else:
            (r0, c0), (r1, c1) = o["top_left"], o["bottom_right"]
            r0, r1 = sorted((r0, r1))
            c0, c1 = sorted((c0, c1))
            fill = o.get("fill", False)
            for r in range(r0, r1 + 1):
                for c in range(c0, c1 + 1):
                    if fill or r in (r0, r1) or c in (c0, c1):
                        g[r][c] = t
    return ["".join(r) for r in g]


def grid_text(grid):
    return "\n".join(f"{i:2d} {row}" for i, row in enumerate(grid))


def stage_fine(place, terrain, grid, logger, seed):
    legend = ", ".join(f"{t['symbol']}={t['name']}" for t in terrain)
    syms = {t["symbol"] for t in terrain}
    prompt = f"""We are building a 2D tile map of this place: "{place}".
Terrain legend: {legend}
Current map, {H} rows by {W} columns (each line starts with its row number, row 0 is north, column 0 is west):
{grid_text(grid)}

Fourth step: add the linear and structural features the place needs — paths between areas, a river course, walls of a building, a shoreline detail. You paint by listing draw operations that are applied in order.

Reply with only a JSON object in exactly this shape:
{OPS_SKELETON}

Op meanings:
- "line": paints the tile along a straight line from [row, col] to [row, col], inclusive.
- "rect": paints a rectangle between the two corners; "fill": true paints the inside too, "fill": false paints only the border.

Rows go 0 to {H-1}, columns 0 to {W-1}. "tile" must be one of: {", ".join(sorted(syms))}.
Use 2 to 10 ops. Keep walkable routes between the main areas of the map."""
    return chat_json([{"role": "user", "content": prompt}], logger, "fine", seed=seed,
                     validator=make_ops_validator(syms))


# ---------- stage 5: placement ----------

def stage_place(place, terrain, items, grid, logger, seed, rng):
    legend = ", ".join(f"{t['symbol']}={t['name']}" for t in terrain)
    want = []
    for d in items:
        want.append({"symbol": d["symbol"], "name": d["name"], "count": d["count"],
                     "on_terrain": d["on_terrain"]})
    expected = {d["symbol"]: d["count"] for d in items}
    on_terrain = {d["symbol"]: d["on_terrain"] for d in items}

    def validate(obj):
        pl = obj.get("placements")
        if not isinstance(pl, list):
            return "reply needs a placements list"
        counts = {}
        for p in pl:
            s = p.get("symbol")
            if s not in expected:
                return f"symbol '{s}' is not in the item list"
            r, c = p.get("row"), p.get("col")
            if not (isinstance(r, int) and isinstance(c, int) and 0 <= r < H and 0 <= c < W):
                return f"row must be 0..{H-1} and col 0..{W-1}"
            counts[s] = counts.get(s, 0) + 1
        for s, n in expected.items():
            if counts.get(s, 0) != n:
                return f"place exactly {n} of '{s}' (you placed {counts.get(s, 0)})"
        seen = set()
        for p in pl:
            key = (p["row"], p["col"])
            if key in seen:
                return f"two items share the cell {list(key)}; use one item per cell"
            seen.add(key)
        return None

    prompt = f"""We are building a 2D tile map of this place: "{place}".
Terrain legend: {legend}
Current map, {H} rows by {W} columns (each line starts with its row number):
{grid_text(grid)}

Fifth step: place the objects and entities. Items to place (with how many copies and their preferred terrain):
{json.dumps(want)}

Reply with only a JSON object in exactly this shape:
{{
  "placements": [
    {{"symbol": "h", "row": 4, "col": 21}}
  ]
}}

Place exactly the requested count of each symbol, one item per cell. Read the map above and put each item on its preferred terrain letter, in a spot that makes sense for the place (market stalls cluster together, a hermit hut sits away from paths, fishermen stand near water)."""
    result = chat_json([{"role": "user", "content": prompt}], logger, "place", seed=seed, validator=validate)
    placements = result["placements"]
    # snap items sitting on wrong terrain to nearest cell of preferred terrain
    snapped = 0
    taken = {(p["row"], p["col"]) for p in placements}
    for p in placements:
        pref = on_terrain[p["symbol"]]
        if grid[p["row"]][p["col"]] == pref:
            continue
        best = None
        for r in range(H):
            for c in range(W):
                if grid[r][c] == pref and (r, c) not in taken:
                    d = abs(r - p["row"]) + abs(c - p["col"])
                    if best is None or d < best[0]:
                        best = (d, r, c)
        if best:
            taken.discard((p["row"], p["col"]))
            p["row"], p["col"] = best[1], best[2]
            taken.add((best[1], best[2]))
            snapped += 1
    return placements, snapped


# ---------- stage 6: self-critique rounds ----------

def stage_critique(place, terrain, grid, placements, items, logger, seed):
    legend = ", ".join(f"{t['symbol']}={t['name']}" for t in terrain)
    item_legend = ", ".join(f"{d['symbol']}={d['name']}" for d in items)
    pl_txt = json.dumps(placements)
    prompt = f"""You are reviewing a finished 2D tile map of this place: "{place}".
Terrain legend: {legend}
Item legend: {item_legend}
Map, {H} rows by {W} columns (each line starts with its row number):
{grid_text(grid)}
Item placements: {pl_txt}

Judge the map against the place description. Reply with only a JSON object in exactly this shape:
{{
  "score": 7,
  "issues": [
    "the market stalls are scattered instead of forming a market square"
  ]
}}

"score" is 1 to 10 for how well the map matches the place. "issues" lists concrete problems worth fixing, each mentioning specific rows and columns where possible. An empty issues list is a valid answer when the map is good."""
    def validate(obj):
        if not isinstance(obj.get("score"), int) or not isinstance(obj.get("issues"), list):
            return 'reply needs an integer "score" and an "issues" list'
        return None
    return chat_json([{"role": "user", "content": prompt}], logger, "critique", seed=seed, validator=validate)


def stage_fix(place, terrain, grid, placements, items, issues, logger, seed):
    legend = ", ".join(f"{t['symbol']}={t['name']}" for t in terrain)
    syms = {t["symbol"] for t in terrain}
    item_syms = {d["symbol"] for d in items}
    prompt = f"""We are fixing a 2D tile map of this place: "{place}".
Terrain legend: {legend}
Map, {H} rows by {W} columns (each line starts with its row number):
{grid_text(grid)}
Item placements: {json.dumps(placements)}
Issues found in review:
{json.dumps(issues, indent=2)}

Reply with only a JSON object in exactly this shape:
{{
  "ops": [
    {{"op": "line", "tile": "P", "from": [2, 3], "to": [18, 3]}},
    {{"op": "rect", "tile": "W", "top_left": [5, 10], "bottom_right": [9, 20], "fill": false}}
  ],
  "moves": [
    {{"symbol": "h", "from": [4, 21], "to": [10, 12]}}
  ]
}}

"ops" repaint terrain (line paints along a straight line, rect paints a border, or the whole box with "fill": true). "moves" relocate one placed item from its current cell to a new cell. Rows go 0 to {H-1}, columns 0 to {W-1}. Terrain tiles: {", ".join(sorted(syms))}. Item symbols: {", ".join(sorted(item_syms))}. Empty lists are valid for anything that needs no change. Address the listed issues with the fewest edits that fix them."""

    ops_validate = make_ops_validator(syms)

    def validate(obj):
        err = ops_validate({"ops": obj.get("ops", [])})
        if err:
            return err
        moves = obj.get("moves", [])
        if not isinstance(moves, list):
            return "moves must be a list"
        for m in moves:
            if m.get("symbol") not in item_syms:
                return f"move symbol must be one of {sorted(item_syms)}"
            if not (_valid_pt(m.get("from")) and _valid_pt(m.get("to"))):
                return "each move needs from and to as [row, col] inside the map"
        return None

    return chat_json([{"role": "user", "content": prompt}], logger, "fix", seed=seed, validator=validate)


def apply_moves(placements, moves):
    applied = 0
    for m in moves:
        for p in placements:
            if p["symbol"] == m["symbol"] and [p["row"], p["col"]] == m["from"]:
                p["row"], p["col"] = m["to"][0], m["to"][1]
                applied += 1
                break
    return applied


# ---------- driver ----------

def compute_checks(grid, terrain, placements, items):
    walkable_syms = {t["symbol"] for t in terrain if t["walkable"]}
    obj_walk = {}
    walk_flag = {d["symbol"]: d.get("walkable", True) for d in items}
    for p in placements:
        obj_walk[(p["row"], p["col"])] = walk_flag.get(p["symbol"], True)
    return walkable_stats(grid, walkable_syms, obj_walk)


def generate_map(place, seed, out_prefix, critique_rounds=2):
    rng = random.Random(seed)
    logger = TranscriptLogger(f"{out_prefix}_transcript.jsonl")
    t0 = time.time()

    tileset = stage_tileset(place, logger, seed)
    terrain = tileset["terrain"]
    for i, t in enumerate(terrain):
        t["color"] = parse_color(t.get("color"), i)

    obj_spec = stage_objects(place, terrain, logger, seed)
    items = obj_spec["objects"] + obj_spec["entities"]

    coarse = stage_coarse(place, terrain, logger, seed)
    walkable_syms = {t["symbol"] for t in terrain if t["walkable"]}
    grid = upscale_and_smooth(coarse["rows"], walkable_syms, rng)

    fine = stage_fine(place, terrain, grid, logger, seed)
    grid = apply_ops(grid, fine["ops"])

    placements, snapped = stage_place(place, terrain, items, grid, logger, seed, rng)

    history = [{"stage": "initial", "checks": compute_checks(grid, terrain, placements, items)}]
    for rnd in range(critique_rounds):
        critique = stage_critique(place, terrain, grid, placements, items, logger, seed)
        entry = {"stage": f"critique_{rnd}", "score": critique["score"], "issues": critique["issues"]}
        if critique["issues"]:
            fix = stage_fix(place, terrain, grid, placements, items, critique["issues"], logger, seed)
            grid = apply_ops(grid, fix.get("ops", []))
            moved = apply_moves(placements, fix.get("moves", []))
            entry["ops_applied"] = len(fix.get("ops", []))
            entry["moves_applied"] = moved
        entry["checks"] = compute_checks(grid, terrain, placements, items)
        history.append(entry)
        if not critique["issues"]:
            break

    wall = round(time.time() - t0, 1)
    result = {
        "place": place,
        "seed": seed,
        "terrain": terrain,
        "items": items,
        "grid": grid,
        "placements": placements,
        "snapped_placements": snapped,
        "history": history,
        "cost": {
            "calls": logger.calls,
            "prompt_tokens": logger.prompt_tokens,
            "completion_tokens": logger.completion_tokens,
            "wall_seconds": wall,
        },
    }
    with open(f"{out_prefix}_map.json", "w") as f:
        json.dump(result, f, indent=1)
    return result
