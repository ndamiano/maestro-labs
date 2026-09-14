# 5. CHARACTERS

**Player.** Silhouette: a small, warm, curious collector — cream shirt, brown vest, straw/wool hat (silhouette hat), small canvas satchel/basket, simple legs; no weapon, no complex facial detail. Smaller than most nodes/furniture so the world feels larger. Sprite 16×16 centered in a 24×24 tile; shadow 12×6 soft ellipse.

Facings: **8 directions** for idle/walk (supports diagonal movement); **4 cardinal directions** for action animations (berry pick, mine, fish set) — actions are less frequent; this bounds the animation set.

Animations (frame = `floor(time × fps) % frames`; reduce motion ⇒ static frame 0 for idle/walk only):

| State | Frames | FPS | Motion rule |
| --- | ---: | ---: | --- |
| Idle | 2 | 4 | Gentle breathing, subtle bob |
| Walk | 4 | 8 | Short step, 8-dir |
| Berry Pick | 2 | 8 | Reaches toward the bush; faces cardinal toward target |
| Mine | 2 | 8 | Pick swings down |
| Fish Cast | 2 | 12 | Rod extends; line + bobber drawn to water |
| Fish Wait | 2 | 4 | Holding rod |
| Fish Strike | 1 | 12 | Rod snaps forward |
| Fish Catch | 2 | 12 | Small celebration |
| Fish Fail | 2 | 12 | Rod relaxes |

Feedback: gathering ⇒ resource icon pops toward player with `+1`/`+2`; targeted object ⇒ soft white outline + slight brightening; `Bag Full` ⇒ red prompt; fishing ⇒ rod line visible.

**Shopkeepers (3).** Shared painterly style; distinct silhouettes and category accents; each has a small overhead canopy/sign (canopy color: Moss berry red/green, Grit copper/stone, Reed blue/teal) and a category icon (berry / pick / fish). The Trading Post is open-air — three stalls, no closed building.

| Keeper | Silhouette | Colors | Costume |
| --- | --- | --- | --- |
| Moss | Rounded, soft | Soft green, leaf brown, cream | Leaf-like hood / small plant hat |
| Grit | Broader, sturdier | Brown, copper, grey | Sturdy coat, tool belt |
| Reed | Longer, relaxed | Blue, teal, pale straw | Loose poncho, straw hat |

Animations: Idle 2f@4 (T1); Talk 2f@8, Sell 1f@12, Buy 1f@12, Unlock 2f@12 (T3).

**Node/fish visual states** (states gameplay rules need): berry full (visible clusters — one cluster if count 1, two if 2; tier color; glow for Ember) / empty (bare branches, muted) / picking (shake once, berry pop) / respawn (fade-in 0.3s); ore 3/2/1/0 charges (intact → chip → large crack → hollow dark interior; tier speckles: copper brown-orange, silver pale, crystal cyan facets + slow glow) / mining (shake, 2–3 chips, icon pop, crack grows) / respawn (cracks close, mineral fades in 0.3s); fish spot idle (small ripple ring every 2–3s, faint slow fish shadow, low contrast) / in range (slight highlight) / casting (line + bobber) / waiting (bobber bobs) / bite (sharp dip, expanding ripple, small splash, prompt `Strike!`) / catch (splash, fish icon pop, soft ring) / fail (dull splash, line flicks, one-frame desaturation) / cooldown (no major animation).
