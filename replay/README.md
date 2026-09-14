# replay lab — what the replay tool has measured

The tool lives in `lib/replay/` (see its README). This folder holds the arms and run scripts of
each question asked with it, and the answers.

## What it has measured

- **The file-state block does nothing.** 18 samples an arm over six real compaction points: 8/18
  turns re-read with the block, 9/17 without. Nor did four other attacks on the same turn — a rule
  instead of a fact, no code map at all, the file bodies pasted into the note, and the bodies
  delivered as a completed `read_file` round. The last is the informative one: handing the model
  the exact bytes it would have read does not stop it reading them.
- **Turns that overrun are an inference failure, not a transcript one.** The six positions where
  one build ran the window dry fail 2 times in 36 when replayed, and the 105,867-token worst case
  resamples to a median of 1,838. The cut-off nudge is what carries it forward: 14,160 tokens with
  that exchange in context against 1,934 without. Shipped as maestro f430496.
- **Where the tokens are is not where they look.** On the 27B locally: writing 34%, reading 31%,
  turns that emitted nothing 17%. On prod Flash-Next: reading 52%, writing 34%, nothing-emitted
  2.5% — and 77% of prod's reads are of files already read. Fix builds are what read: they start
  with an empty transcript and have to read the game back.

## Not built yet

- k-turn branching, for questions a single turn cannot answer. A replay is faithful to the turn it
  starts from; after one turn the trajectory is its own.
- Anything measured against Flash-Next. Every arm here ran on the local 27B, and prod's read rate
  is worse than the one the null results were measured against.
