"""Programmatic map checks: connectivity, walkable fraction, entity presence."""
from collections import deque


def walkable_stats(grid, walkable_symbols, object_cells=None):
    """grid: list of strings. object_cells: {(r,c): walkable_bool} overrides."""
    object_cells = object_cells or {}
    h, w = len(grid), len(grid[0])

    def is_walkable(r, c):
        if (r, c) in object_cells:
            return object_cells[(r, c)]
        return grid[r][c] in walkable_symbols

    walkable = [(r, c) for r in range(h) for c in range(w) if is_walkable(r, c)]
    total = h * w
    if not walkable:
        return {"walkable_frac": 0.0, "largest_component_frac": 0.0, "n_components": 0}

    seen = set()
    components = []
    for cell in walkable:
        if cell in seen:
            continue
        comp = 0
        q = deque([cell])
        seen.add(cell)
        while q:
            r, c = q.popleft()
            comp += 1
            for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nr, nc = r + dr, c + dc
                if 0 <= nr < h and 0 <= nc < w and (nr, nc) not in seen and is_walkable(nr, nc):
                    seen.add((nr, nc))
                    q.append((nr, nc))
        components.append(comp)
    components.sort(reverse=True)
    return {
        "walkable_frac": round(len(walkable) / total, 3),
        "largest_component_frac": round(components[0] / len(walkable), 3),
        "n_components": len(components),
    }
