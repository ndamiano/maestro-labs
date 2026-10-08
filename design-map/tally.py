"""Morning tally, one row per overnight run: did the builder use the design by range, read section
9, name its tests after the design's, finish, and what the gates said.

    PYTHONPATH=.. ../../venv/bin/python tally.py [run id ...]      default: builds.tsv
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lib.paths import RUNS  # noqa: E402

DESIGN_TESTS = re.compile(r"`([a-z]+: [^`]+)`")
DESIGN_READ = re.compile(r"read_file\(\s*['\"]design/design\.md['\"]\s*(?:,\s*(?:offset\s*=\s*)?(\d+))?")


def section_lines(text, title_rx):
    lines = text.splitlines()
    heads = [(i + 1, len(m.group(1)), m.group(2)) for i, l in enumerate(lines)
             if (m := re.match(r"^(#{1,6})\s+(.*)", l))]
    for k, (ln, lvl, t) in enumerate(heads):
        if re.search(title_rx, t):
            end = next((ln2 - 1 for ln2, lvl2, _ in heads[k + 1:] if lvl2 <= lvl), len(lines))
            return ln, end
    return None


def tally(rid):
    run = RUNS / rid
    rows = [json.loads(l) for l in open(run / "turns.jsonl", encoding="utf-8")]
    design = (run / "game/design/design.md").read_text(encoding="utf-8") if (run / "game/design/design.md").exists() else ""
    sec9 = section_lines(design, r"TESTS") if design else None
    out = {"run": rid, "builds": 0, "turns": 0, "compacts": 0, "design_whole": 0, "design_ranged": 0,
           "sec9_reads": 0, "plays": 0, "presses": 0, "done": None, "cap": None}
    bid = None
    for r in rows:
        if r["kind"] == "meta":
            bid = r["build_id"]; out["builds"] += 1
            if out["builds"] == 1:
                out["cap"] = None
            continue
        if bid != rows[0]["build_id"]:
            continue
        if r["kind"] == "compact":
            out["compacts"] += 1; continue
        if r["kind"] != "turn":
            continue
        out["turns"] += 1
        resp = r["response"]; msg = resp["choices"][0]["message"] if "choices" in resp else resp
        code = ""
        for tc in msg.get("tool_calls") or []:
            try: code += json.loads(tc["function"]["arguments"]).get("code", "")
            except Exception: code += tc["function"]["arguments"]
        for m in DESIGN_READ.finditer(code):
            if m.group(1) is None:
                out["design_whole"] += 1
            else:
                out["design_ranged"] += 1
                if sec9 and sec9[0] - 5 <= int(m.group(1)) <= sec9[1]:
                    out["sec9_reads"] += 1
        out["plays"] += len(re.findall(r"\bplay\(", code))
        out["presses"] += code.count("__press")
        if re.search(r"\bdone\(", code):
            out["done"] = r["turn"]
    st = json.loads((run / "build_state.json").read_text()) if (run / "build_state.json").exists() else {}
    out["state"] = f"{st.get('kind')} {st.get('phase')} step {st.get('step')} ok={st.get('ok')} cap={st.get('max_steps')}"
    sec = "\n".join(design.splitlines()[sec9[0] - 1:sec9[1]]) if sec9 else ""
    names = {n for n in re.findall(r"`([^`\n]{4,})`", sec) if " " in n or "_" in n or ":" in n}
    written, srcs = 0, ""
    for p in sorted((run / "game").rglob("*.js")):
        if "test" not in p.name.lower() and "tests" not in p.parts:
            continue
        src = p.read_text(encoding="utf-8", errors="replace"); srcs += src
        written += len(re.findall(r"""\btest\(\s*['"]|name:\s*['"]|^\s*['"][^'"]{6,}['"]\s*:\s*(?:async\s*)?(?:\(|function)""", src, re.M))
    hits = sum(n in srcs for n in names)
    out["tests_written"] = written; out["design_test_names"] = f"{hits}/{len(names)}"
    for gate in ("error_gate", "play_gate"):
        p = run / f"{gate}.json"
        out[gate] = json.loads(p.read_text()) if p.exists() else None
    rep = run / "play_report.json"
    if rep.exists():
        j = json.loads(rep.read_text())
        out["play_broken"] = [b["action"] for b in j.get("broken", [])]
        out["play_works"] = (j.get("judgment") or {}).get("works", "")[:300]
    return out


if __name__ == "__main__":
    rids = sys.argv[1:] or [l.split("\t")[1] for l in open(Path(__file__).parent / "builds.tsv") if len(l.split("\t")) > 2]
    for rid in rids:
        try:
            print(json.dumps(tally(rid), indent=1))
        except Exception as e:
            print(rid, "tally failed:", e)
