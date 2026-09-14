"""Per arm: time to first token against prompt tokens, cache-hit fraction, wall — from a results
dir written by arms.sh. Prints a table and writes ttft.png when matplotlib is there."""
import json
import statistics
import sys
from collections import defaultdict
from pathlib import Path


def load(d):
    rows = []
    for f in sorted(Path(d).glob("*.jsonl")):
        rows += [json.loads(l) for l in open(f)]
    return rows


def bucket(pt):
    return f"{int(pt // 20000) * 20}K"


def main(d):
    rows = load(d)
    arms = defaultdict(list)
    for r in rows:
        arms[r["arm"]].append(r)
    for arm, rs in arms.items():
        ok = [r for r in rs if not r["error"] and r["ttft"] is not None]
        errs = [r for r in rs if r["error"]]
        wall = max(r["t_start"] + r["total"] for r in rs) if rs else 0
        cached = [r["cached_tokens"] / r["prompt_tokens"] for r in ok
                  if r.get("cached_tokens") is not None and r["prompt_tokens"]]
        print(f"\n== {arm}: {len(rs)} turns, {len(errs)} errors, wall {wall / 60:.1f} min, "
              f"cached fraction median {statistics.median(cached):.2f}" if cached else
              f"\n== {arm}: {len(rs)} turns, {len(errs)} errors, wall {wall / 60:.1f} min, no cache report")
        by = defaultdict(list)
        for r in ok:
            by[bucket(r["prompt_tokens"])].append(r)
        print(f"{'prompt':>8} {'n':>4} {'ttft p50':>9} {'ttft p90':>9} {'uncached p50':>13} {'misses>20K':>11}")
        for b in sorted(by, key=lambda s: int(s[:-1])):
            xs = by[b]
            tt = sorted(r["ttft"] for r in xs)
            unc = sorted(r["prompt_tokens"] - (r["cached_tokens"] or 0) for r in xs)
            miss = sum(1 for u in unc if u > 20000)
            print(f"{b:>8} {len(xs):>4} {tt[len(tt) // 2]:>9.2f} {tt[int(len(tt) * .9)]:>9.2f} "
                  f"{unc[len(unc) // 2]:>13} {miss:>11}")
        for r in errs[:5]:
            print("  err", r.get("run", r.get("stream")), r["turn"], r["error"][:120])
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9, 5))
        for arm, rs in arms.items():
            ok = [r for r in rs if not r["error"] and r["ttft"] is not None]
            ax.scatter([r["prompt_tokens"] for r in ok], [r["ttft"] for r in ok], s=8, label=arm, alpha=.6)
        ax.set_xlabel("prompt tokens"); ax.set_ylabel("time to first token (s)"); ax.set_yscale("log")
        ax.legend(); fig.tight_layout(); fig.savefig(Path(d) / "ttft.png", dpi=120)
        print("\nwrote", Path(d) / "ttft.png")
    except ImportError:
        pass


if __name__ == "__main__":
    main(sys.argv[1])
