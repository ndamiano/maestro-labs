"""A lab design through the PROD design path: design.enqueue lands the text as a run's prompt via
the control plane's completion handler (which then auto-starts the build). One-shot: the run
builds. Team: three designer runs (their auto-builds abandoned on landing), then the integrator's
run, which builds. Usage: design_prod.py <skel|team|integrate|both> <slug>; both = all four designer jobs enqueued at once  → prints the run id that builds."""
import json, re, sys, time
from pathlib import Path
sys.path.insert(0, "/home/nick/Documents/ai-agent-test/src")
from auth import store
from billing.packages import MICROS_PER_CREDIT
from db import games, jobs
from maestro.codegen import design, build_chain
from maestro.codegen.run import create_run, open_ask
from maestro.state import RunState

LAB = Path("/home/nick/Documents/ai-agent-test/labs/spec-skeleton")
arm, slug = sys.argv[1], sys.argv[2]
ask = dict(json.load(open(LAB / "asks.json")))[slug]
user = store.list_users()[0].id


def esc(s: str) -> str:
    return s.replace("{", "{{").replace("}", "}}")


SECTIONS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "A"]


def missing_sections(text: str) -> list:
    """Major headings the integrated spec must carry; subsections are free to be skipped."""
    have = set(re.findall(r"^#\s*(\d+|A)\.", text, re.M))
    return [n for n in SECTIONS if n not in have]


def start(prompt_text: str, tag: str) -> str:
    """Enqueue one design through the prod path. prompt_text keeps {request}; everything else is literal."""
    tmp = LAB / "tmp" / f"{slug}.{tag}.prompt.txt"
    tmp.write_text(prompt_text)
    design._PROMPT = tmp
    rid = create_run(user); games.charge_game(rid, 0, MICROS_PER_CREDIT); open_ask(rid, ask)
    design.enqueue(rid, ask)
    print(f"{tag}: run {rid} design job enqueued", flush=True)
    return rid


def await_all(started: dict, keep_build: set) -> dict:
    """started = {tag: rid}. Polls every run until its design lands; returns {tag: text}."""
    t0 = time.time(); texts = {}
    while len(texts) < len(started):
        for tag, rid in started.items():
            if tag in texts:
                continue
            req = (RunState(rid).read_spec() or {}).get("request") or ""
            if not req.strip():
                continue
            if req.strip() == ask.strip():
                raise SystemExit(f"{tag}: design landed EMPTY (the ask became the prompt) after {time.time()-t0:.0f}s")
            print(f"{tag}: {len(req)} chars landed in {time.time()-t0:.0f}s", flush=True)
            (LAB / "designs" / "team" / f"{slug}.{tag}.prod.md").write_text(req)
            texts[tag] = req
            if tag not in keep_build:
                stopped = build_chain.stop(rid)
                n = jobs.abandon_game_jobs(rid, "lab: intermediate design, no build")
                print(f"{tag}: auto-build stopped={stopped} ({n} job(s) abandoned)", flush=True)
        if time.time() - t0 > 3600:
            raise SystemExit(f"nothing landed for {set(started) - set(texts)} in 1 h")
        time.sleep(3)
    return texts


def integrate_prompt(docs: dict) -> str:
    tmpl = open(LAB / "variants" / "team_integrate.txt").read()
    return tmpl.replace("{gameplay}", esc(docs["gameplay"])).replace("{visual}", esc(docs["visual"])).replace("{engineering}", esc(docs["engineering"]))


def integrate(docs: dict, tries: int = 3) -> tuple:
    """Integrator with a section gate: a spec missing a major heading is abandoned and re-run."""
    for i in range(1, tries + 1):
        tag = f"integrate{i}"
        rid = start(integrate_prompt(docs), tag)
        text = await_all({tag: rid}, keep_build={tag})[tag]
        gap = missing_sections(text)
        if not gap:
            print(f"{tag}: section gate PASS", flush=True)
            return rid, text
        print(f"{tag}: section gate FAIL, missing {gap}; abandoning run {rid}", flush=True)
        build_chain.stop(rid); jobs.abandon_game_jobs(rid, f"lab: spec missing sections {gap}")
    raise SystemExit(f"integrator failed the section gate {tries} times")


def integrate_split(docs: dict) -> str:
    """Two integrator calls: sections 0-8, then 9-A continuing the first; each stays under the
    ~20K output tokens Flash-Next ends a response at. Nothing builds; the text is returned."""
    p1 = open(LAB / "variants" / "team_integrate_p1.txt").read()
    for r in ROLES:
        p1 = p1.replace("{" + r + "}", esc(docs[r]))
    first = await_all({"int_p1": start(p1, "int_p1")}, keep_build=set())["int_p1"]
    p2 = open(LAB / "variants" / "team_integrate_p2.txt").read().replace("{spec_so_far}", esc(first))
    for r in ROLES:
        p2 = p2.replace("{" + r + "}", esc(docs[r]))
    second = await_all({"int_p2": start(p2, "int_p2")}, keep_build=set())["int_p2"]
    text = first.rstrip() + "\n\n" + second.lstrip()
    gap = missing_sections(text)
    print(f"split integrator: {len(first)} + {len(second)} chars; section gate {'PASS' if not gap else 'FAIL ' + str(gap)}", flush=True)
    if gap:
        raise SystemExit("split integrator failed the section gate")
    return text


def integrate_cont(docs: dict, text: str, rounds: int = 5) -> str:
    """Continuation loop: the spec so far goes back with 'continue from where it ends' until the
    section gate passes. Each call ends at Flash-Next's ~20K-token output stop wherever that is."""
    for i in range(1, rounds + 1):
        gap = missing_sections(text)
        if not gap:
            print(f"cont: section gate PASS after {i-1} continuation(s), {len(text)} chars", flush=True)
            return text
        print(f"cont {i}: missing {gap}, {len(text)} chars so far", flush=True)
        p = open(LAB / "variants" / "team_integrate_cont.txt").read().replace("{spec_so_far}", esc(text))
        for r in ROLES:
            p = p.replace("{" + r + "}", esc(docs[r]))
        more = await_all({f"cont{i}": start(p, f"cont{i}")}, keep_build=set())[f"cont{i}"]
        text = text.rstrip() + "\n" + more.strip() + "\n"
    raise SystemExit(f"cont: gate still failing {missing_sections(text)} after {rounds} rounds")


ROLES = ("visual", "gameplay", "engineering")
if arm == "cont":
    docs = {r: (LAB / "designs" / "team" / f"{slug}.{r}.prod.md").read_text() for r in ROLES}
    text = integrate_cont(docs, (LAB / "designs" / "team" / f"{slug}.int_p1.prod.md").read_text())
    (LAB / "designs" / f"{slug}.team_cont.prod.md").write_text(text)
    print(f"design written: designs/{slug}.team_cont.prod.md (build it with build.sh)", flush=True)
    raise SystemExit(0)
if arm == "split":
    docs = {r: (LAB / "designs" / "team" / f"{slug}.{r}.prod.md").read_text() for r in ROLES}
    text = integrate_split(docs)
    (LAB / "designs" / f"{slug}.team_split.prod.md").write_text(text)
    print(f"design written: designs/{slug}.team_split.prod.md (build it with build.sh)", flush=True)
    raise SystemExit(0)
if arm == "integrate":
    docs = {r: (LAB / "designs" / "team" / f"{slug}.{r}.prod.md").read_text() for r in ROLES}
    rid, text = integrate(docs)
    arm = "team"
elif arm == "skel":
    rid = start(open(LAB / "variants" / "skel.txt").read(), "skel")
    text = await_all({"skel": rid}, keep_build={"skel"})["skel"]
elif arm == "team":
    started = {r: start(open(LAB / "variants" / f"team_{r}.txt").read(), r) for r in ROLES}
    rid, text = integrate(await_all(started, keep_build=set()))
else:
    started = {r: start(open(LAB / "variants" / f"team_{r}.txt").read(), r) for r in ROLES}
    started["skel"] = start(open(LAB / "variants" / "skel.txt").read(), "skel")
    docs = await_all(started, keep_build={"skel"})
    (LAB / "designs" / f"{slug}.skel.prod.md").write_text(docs["skel"])
    print(f"skel: building run {started['skel']}", flush=True)
    rid, text = integrate(docs)
    arm = "team"
(LAB / "designs" / f"{slug}.{arm}.prod.md").write_text(text)
print(f"design written: designs/{slug}.{arm}.prod.md; building run {rid}", flush=True)
print(f"run: {rid} {slug} — {arm} design on Flash-Next (prod pods)", flush=True)
