# launch-battery

Status: battery
Control: 2026-09-06 "Stage 1 on prod: six one-shot games" (pre design team); 2026-09-14 spec-skeleton
and 2026-09-15 design-map batteries (design team, local 27B only).

## Purpose

Google Playground launched 2026-10-07: free, Gemini + Nano Banana + Lyria, US 18+ only. Nick played
its gallery: more coherent, better sound, better art, better feel than ours. The design team
(3e05254) and design-in-the-code-map (90d82c3) are on prod and have never been played there — the
last prod games predate both. Before a Reddit launch we need to know what a stranger gets today,
and we need the best of it as launch material.

## Hypothesis

No change to the loop. Measured: per game, runs/crashes, done vs capped, steps, cost, and Nick's
play verdict on coherence, sound, art, feel. Expected from the local batteries: most run, roughly
half finish under the cap, content (levels, first minute) and sound are the weak axes. A result
where most games fail to run would mean prod regressed and blocks launch.

## Setup

Prod as deployed (Flash-Next on SGLang, RTX PRO 6000), front door, one ask per game, no change notes.
Asks are written the way a stranger types:

1. `3d kart racing on a candy planet, drifting and item boxes`
2. `roguelike deckbuilder where you're a wizard cat climbing a tower`
3. `cozy farming game but the crops are weird alien plants`
4. `murder mystery visual novel on a night train`
5. `bullet hell where you're a bee defending the hive`
6. `zombie game but you're the zombie lol`

## Log

**2026-10-07 12:30.** Six asks entered through the front door: kart e39dbca3af5e, rogue
3e4f28885cfd, farm 94700c528d27, mystery 0627d0a2a956, bullet f4c1a36909a6, zombie 0de96eecb39c.
Every llm rung refused for ~40 min (RunPod PRO 6000 WK+SE on both volumes, EC2 g7e us-west-2 and
eu-north-1, spot and on-demand) before one RunPod 6000 landed; the six then design two at a time.
Capacity is a launch blocker alongside quality: a Reddit spike during a stock-out builds nothing.

## Outcome
