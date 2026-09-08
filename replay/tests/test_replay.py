import json

import pytest

import replay


def _log(tmp_path, records):
    run = tmp_path / "src_run"
    (run / "game").mkdir(parents=True)
    with (run / "turns.jsonl").open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return run


def _turn(n, code, tool_result=""):
    return {"kind": "turn", "turn": n, "job_id": f"j{n}",
            "added": ([{"role": "tool", "content": tool_result}] if tool_result else []),
            "response": {"tool_calls": [{"id": f"c{n}", "function": {
                "name": "python", "arguments": json.dumps({"code": code})}}]},
            "usage": {}, "exec_seconds": 1.0, "error": None}


def test_a_replay_that_ran_nothing_reports_unknown_fidelity_not_perfect(tmp_path):
    """The failure that matters: a broken replay whose programs never ran agrees with every
    recording, and must never call itself faithful."""
    r = replay.Replay(run_dir=tmp_path, position=1, messages=[], system="", tools=[])
    r.turns = [replay.Turn(turn=1, programs=1, recorded="x", replayed="", matched=True,
                           evidence=False, error="the program produced neither output nor a tool call")]
    assert r.fidelity is None
    assert r.errors and not r.diverged


def test_fidelity_counts_only_turns_that_could_disagree(tmp_path):
    r = replay.Replay(run_dir=tmp_path, position=9, messages=[], system="", tools=[])
    r.turns = [
        replay.Turn(turn=1, programs=1, recorded="hello", replayed="hello", matched=True, evidence=True),
        replay.Turn(turn=2, programs=1, recorded="hello", replayed="nope", matched=False, evidence=True),
        replay.Turn(turn=3, programs=1, recorded="", replayed="", matched=True, evidence=False),
    ]
    assert r.fidelity == 0.5
    assert [t.turn for t in r.diverged] == [2]


def test_a_replay_refuses_to_write_into_an_existing_directory(tmp_path):
    run = _log(tmp_path, [{"kind": "meta", "build_id": "b", "system": "s", "tools": []}])
    (tmp_path / "target").mkdir()
    with pytest.raises(FileExistsError):
        replay.run_to_position(run, 1, tmp_path / "target")


def test_the_source_run_is_never_written_to(tmp_path):
    run = _log(tmp_path, [{"kind": "meta", "build_id": "b", "system": "s", "tools": []},
                          _turn(1, "print('hi')", "hi")])
    before = {p.name: p.stat().st_mtime_ns for p in run.rglob("*") if p.is_file()}
    replay.run_to_position(run, 1, tmp_path / "t")
    after = {p.name: p.stat().st_mtime_ns for p in run.rglob("*") if p.is_file()}
    assert before == after


def test_landing_schedule_reads_the_turn_an_asset_reached_its_final_size(tmp_path):
    run = tmp_path / "r"
    (run / "game" / "assets").mkdir(parents=True)
    art = run / "game" / "assets" / "hero.webp"
    art.write_bytes(b"x" * 500)
    records = [
        _turn(1, "print(list_files())", "[{'path': 'assets/hero.webp', 'bytes': 40}]"),
        _turn(2, "print(list_files())", "[{'path': 'assets/hero.webp', 'bytes': 500}]"),
        _turn(3, "print('done')", "done"),
    ]
    schedule = replay._landing_schedule(records, run / "game")
    # Turn 1 saw a stand-in; the real render is only in evidence from turn 2.
    assert schedule == {"assets/hero.webp": 2}


def test_an_asset_never_listed_has_no_landing_turn(tmp_path):
    run = tmp_path / "r"
    (run / "game" / "assets").mkdir(parents=True)
    (run / "game" / "assets" / "hero.webp").write_bytes(b"x" * 500)
    assert replay._landing_schedule([_turn(1, "print('nothing')", "nothing")], run / "game") == {}


def test_agreement_is_containment_not_equality():
    # The recorded message wraps the program's output in the turn's ledger.
    assert replay._agrees("ran 2 tools\nhello\nwrote main.js", "hello")
    assert not replay._agrees("ran 2 tools\nhello", "goodbye")


def test_a_turn_that_printed_nothing_carries_no_evidence():
    assert replay._agrees("anything at all", "")
