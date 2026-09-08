# Why a build writes its own audio, and its own paths

Two defects out of one prod game (`0df4c0941141`, Firefox):

    Uncaught TypeError: setting getter-only property "Q"
        noise  audio.js:33     footstep  audio.js:57     update  state.js:592

`noise` and `footstep` are not in `lib/audio.js`. The game wrote its own WebAudio layer and set
`BiquadFilterNode.Q = 8` — `Q` is a read-only `AudioParam` holding the value, so the write throws.
It is the same in both engines and in module code, which every game's is (measured here: chromium
"Cannot set property Q of #<BiquadFilterNode> which has only a getter", firefox "setting
getter-only property \"Q\""); in a classic non-module script it is silently ignored instead.

## What the corpus says

`runtime/games`, the 99 games built since `lib/` was seeded:

| lib | imported by | hand-rolled instead |
|---|---|---|
| input.js | 88 | 11 |
| canvas.js | 75 | 24 |
| **audio.js** | **49** | **50** |

and, counted by what a game's own files contain:

    lib/audio.js alone:            0 of 99
    lib/audio.js + own WebAudio:  49
    own WebAudio only:            81
    silent:                       77

**No game has ever shipped on lib/audio.js alone.** So this is not adoption failing in general —
`input.js` and `canvas.js` are adopted under the exact same prompt line. It is that `lib/audio.js`
offers eight fixed effect names (`hit pickup jump select fail win shoot explode`), one `tone()` and
a chiptune loop, and the games want a footstep, an engine that rises with speed, a reactor hum, an
alarm. There is no way to ask the lib for those, so the model opens an `AudioContext` — and there
are 189 `createOscillator` and 111 `createBiquadFilter` calls of hand-written WebAudio across the
corpus for a bug like `.Q =` to live in.

Per the capability ladder in CLAUDE.md this is the snippet rung, not a prompt line: the lib is the
thing that is wrong.

## The arms

Design is generated ONCE per ask and handed to both arms, so the only difference is the prompt and
the lib.

- **A — control.** build.txt and lib/audio.js as they ship.
- **D — widened lib + one line.** `lib/audio.js` gains `sound(spec)` (any wave or noise burst,
  pitch/filter sweep, envelope), `noise(ms, opts)`, `seq(notes)` and `loop(spec)` — a held sound
  whose pitch and volume can be changed while it runs, which is what an engine and a hum need. The
  eight named effects and `music` are unchanged and now built on `sound`. build.txt gains one line:

      The game's sound is lib/audio.js. It synthesises whatever the game asks for — a footstep, an
      engine that rises with speed, an alarm — so the game makes no AudioContext of its own.

  Why it should work: the reason the model rolls its own is that the lib cannot make the sound the
  design asks for, and that reason is now gone; the prompt line only has to say that the lib is
  where sound comes from, which is the form `input.js` and `canvas.js` already win with.

Asks are chosen to force game-specific sound (`designs/asks.txt`): footsteps guards can hear, an
engine under strain, a reactor hum.

Scored by `score.py`: does a game's own code import `lib/audio`, how many `AudioContext`s and
oscillators it opens, whether it reaches for the new calls, and whether any `AudioParam` is
assigned directly.

## The path defect, which needed no experiment

The same scan found 2 of 99 games importing `./lib/canvas.js` from `js/main.js` — a module that
404s, so the game never starts. Nothing sees it: the file is valid JavaScript, and a browser
reports a missing module on the console, not as an uncaught exception, so the error gate passes it.

That is BROKEN, not bad, so it is a check and not a prompt line: `check_syntax` now resolves every
local path a game file names (import, `<script src>`, `<link href>`, image `src`) and reports the
ones that are not there, art still queued for rendering excepted. It reads index.html too, since
that is where most of them are. Run over the corpus it flags 8 games: the 2 dead-lib imports and 6
that reference art which never landed — no false positives.

## Why the gate passed it

Not a browser difference. The throw is inside `footstep()`, called from `state.update()` — it
needs the player to MOVE. The gate loads the game, screenshots it and presses what the title
screen offers, and that is deliberately all it does. Everything that only happens once the game is
being played is a human judgement by design, so this stays open, and it is the argument for fixing
the lib rather than the gate: a game that never opens an AudioContext cannot write this bug.
