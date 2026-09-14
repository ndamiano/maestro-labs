# <experiment name>

Status: single-run | battery | control | done | abandoned
Control: <prior runs or experiments.md entries that serve as baseline>

## Purpose

Why this might improve the pipeline. The build, failure, or experiments.md entry that motivated it.
If there is no evidence here, the experiment does not start.

## Hypothesis

What changes. What is measured, and the number it should move. Why the change should move it.
What an idea failure would look like, written before the first run.

## Setup

The diff or prompt change. Which asks, which model and card. The command that runs it from this
folder, so anyone can rerun it.

## Log

Append only. Dated. One entry per run: what ran, the number, a one-line read, and the verdict
(works / implementation fix and rerun / idea failure). Battery and control runs go here too.

## Outcome

Filled at wrap-up. Verdict, what shipped, and the experiments.md section it became. If abandoned,
why.
