# a jailed node tool

Status: single-run
Control: spec-skeleton 2026-09-14: 5/5 engineering docs designed Node test harnesses; 0/6 builds could run one

## Purpose

Every engineering.md put its tests in Node (`node --test`, Vitest, Playwright). The builder's
python tool is seccomp'd (no execve, fork, clone, socket) and has no node tool, so the design's
test plan is dead on arrival and the integrator carries it into §9. Tests-in-files (see
labs/tests-in-files) may make this moot by running everything in the page; this lab is the
other branch.

## Hypothesis

A `node_test(paths)` tool built like pyexec: separate process, empty env, cwd jailed to the game
folder, Node's permission model for fs and child_process, seccomp for the network, a timeout, an
output cap; `--test-isolation=none` (Node 22) so a suite runs in-process. Measured: does the
builder run the designed suite, plays per build, turns to done. Idea failure: the model runs the
suite once and never again, or the jail blocks something node needs on every run.

## Setup

## Log

## Outcome
