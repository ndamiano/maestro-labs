# the post-compaction floor

Status: single-run
Control: spec-skeleton collector c6b51ec35d89 (compactions at 43/83/144/186, 39 design re-reads after 83), the 2026-09-06 re-read-cycle fix (built, unmeasured)

## Purpose

After a compaction a build resumes at ~60K tokens on a 131K window: `_COMPACT_KEEP` 0.33 keeps
the newest body of every game file, and the game is 130–150K chars by then. Each compaction is
followed by re-reads of the spec and the files, and the collector run spent turns 96–199 that
way. Bigger games compact more often and re-read more.

## Hypothesis

A lower keep ratio, or bodies replaced by a file listing plus per-file line counts, drops the
floor and the re-read count without costing the builder what it needs. Measured: turns between
compactions, re-reads per compaction, turns to done, on the collector and platformer specs. Idea
failure: the builder re-reads everything it lost anyway, and the total is the same or worse.

## Setup

## Log

## Outcome
