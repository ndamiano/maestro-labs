# GameSummoner launch

Working doc. Tick as you go.

---

## 1. Check before shouting

### Things the code told me are missing (do these, they gate everything below)

- [ ] **Link preview (OG tags).** `frontend/index.html` has only `<title>GameSummoner</title>`. Every
      post on Reddit/X/Discord/HN unfurls to a blank card. Add: `meta description`, `og:title`,
      `og:description`, `og:image` (1200×630 png, one screenshot of a real built game with the
      wordmark), `og:url`, `twitter:card=summary_large_image`. Test with opengraph.xyz and
      cards-dev.twitter.com/validator before posting anywhere.
- [ ] **Favicon.** None served. Browser tab shows a blank page icon.
- [ ] **`/robots.txt` and `/sitemap.xml`.** Not served. Google can't index landing/about.
- [ ] **A shareable game URL.** `GameView` has embed/tab but I found no public per-game link. The
      viral loop is "look what I made" → a link a stranger can open with no account. If that
      doesn't exist yet, it is the single highest-leverage thing on this list. Even a read-only
      `/g/<run_id>` behind the demo-style public prefix is enough.
- [ ] **HN signup wall.** Show HN guideline: people must be able to try it without signing up. Plan
      (decide): (1) public share URLs + a public gallery so any game is playable with no account;
      (2) a public read-only "watch this build" page (transcript, files, art landing) — HN watches
      the model work, zero credit risk; (3) promo code `HN` = one build's credits, first N
      redemptions, account still required. Credits-start-at-0 stays. Anonymous builds: no.
- [ ] **Demo gallery is the landing pitch.** Make sure the 4–6 demos are the best games the pipeline
      has ever made, load in <2 s, and at least one is 3D. Strangers judge in 5 seconds.

### Product path, done as a stranger (incognito, phone AND desktop)

- [ ] Land → play a demo → sign up → buy smallest package → build → play → send a change note.
- [ ] Sign-up with a throwaway email: verification mail lands in inbox, not spam (check SPF/DKIM/DMARC
      on the sending domain with mail-tester.com).
- [ ] Wrong password / expired token / double-click on Pay: nothing 500s.
- [ ] Credits show 0 on a fresh account and the "buy" path is obvious from there. Credits start at 0
      by decision, so the landing copy or first screen has to say the price BEFORE they sign up, or
      the first post gets "bait and switch" replies.
- [ ] Price is on the landing page in one sentence a person can quote ("a game costs about $X").
- [ ] Stripe live mode: live keys in prod `.env`, webhook endpoint registered on the LIVE dashboard,
      one real card charged and refunded, receipt email says GameSummoner not the Stripe default.
- [ ] Stripe fraud/radar defaults on. Statement descriptor set.
- [ ] Terms/privacy links work from every page (c795330 / 3f3398b — verify in prod, not local).
- [ ] What happens when a build FAILS: user sees a message, credits are refunded or not, and
      that behaviour matches what terms say.

### Ops

- [ ] Uptime monitor on `/healthz` from outside (UptimeRobot / Better Stack free tier), alert to
      phone. One on the pod pool: an alert if llm queue depth > N for > 10 min.
- [ ] Error reporting: a 500 in prod reaches you within minutes. If there's no Sentry, at least
      `docker compose logs` tailed to something you'll see.
- [ ] RunPod spend cap / balance alert. Launch-day traffic × 20 max llm workers × $/hr — write the
      worst-case hourly number down and decide if you're OK with it BEFORE posting.
- [ ] Backups: `data/auth.db`, `data/platform.db`, blobs — one restore rehearsed from the backup,
      not just "backups exist".
- [ ] Droplet RAM headroom (RAM was the wall in the load test). Swap on, or a plan to resize in place.
- [ ] Rate limits on `/api/events`, sign-up, login (bot floods, not users).
- [ ] Landing referrer tracking works in prod (`/api/events/landing`) — you'll want to know which
      channel worked. Add `?ref=hn` style tags to each link you post and record them too.
- [ ] Admin view where you can watch: sign-ups, purchases, builds started/finished/failed, per hour.
      If it's SQL by hand, write the 3 queries now, not on launch day.
- [ ] Every build's ask + result is something you can read the next morning. First 100 asks are the
      most valuable data you'll ever get.

### Content you need in hand before posting

- [ ] 30–60 s screen recording: type the ask, cut to the built game, play it. No narration needed.
      Portrait crop for TikTok/Shorts, landscape for X/Reddit. Real pipeline output, unedited.
- [ ] 6–10 screenshots of different genres (2D platformer, card game, racing, 3D dungeon, rhythm).
- [ ] 3 "before/after" pairs: the one-line ask → the game. These are the post.
- [ ] A one-paragraph honest description (see §3).
- [ ] A support address (support@gamesummoner.com or similar, NOT personal email) that forwards to you.
- [ ] A Discord server or at minimum a place people can report "my build broke". Reddit DMs are not it.

### Legal/identity

- [ ] Business entity / who's on the Stripe account matches who's on the terms.
- [ ] Any user game is potentially copyrighted IP ("make me Mario"). Terms already cover this?
      Have a takedown path in mind (an email is fine).
- [ ] Safety screen is on in prod (`artifact_screen.py`) — a NSFW build screenshot on launch day
      is a bad day.

---

## 2. Where to post

Ordered by expected return for THIS product. Do not do all of it on day one. One channel per
day so you can see what each one does in the referrer log and can actually reply to comments.

### Tier 1 — go here first

| Where | Why | Notes |
|---|---|---|
| **Hacker News (Show HN)** | Right audience for "open-weight model on one card writes real games". Technical honesty wins there. | Post 7–9am ET Tue–Thu. Title: `Show HN: GameSummoner – describe a game, get a playable browser game (open-weight model, one GPU)`. First comment = the technical story: designer stage, no engine, transcript-as-memory, why no judge. Be in the thread all day. |
| **r/IndieGaming, r/gamedev** | Biggest game-making audiences. | gamedev is hostile to "AI made my game" — post as a tool for prototyping, lead with the "any game" framing, expect a fight, be gracious. IndieGaming is friendlier: post the video. |
| **r/artificial, r/singularity, r/LocalLLaMA** | LocalLLaMA will care that it's Qwen on one RTX PRO 6000 more than anything. | LocalLLaMA post is a technical writeup, not an ad. Show the tok/s, the window, the thinking-on finding. They'll ask for the model + prompt; decide now what you're willing to say. |
| **X/Twitter** | Where AI-builders and indie devs hang out. | Thread: video first, then 5–6 screenshots, then the "how". Tag nobody. Post the same video daily with a different game for a week. |
| **Product Hunt** | Sign-ups + backlink. | Needs the OG image, a tagline, 5 gallery images, a maker comment. Launch on a Tue/Wed. Ask 10 people in advance to leave a real comment. |

### Tier 2 — same week

| Where | Notes |
|---|---|
| **TikTok / YouTube Shorts / Instagram Reels** | "I asked AI to make [absurd game]" is a proven format. Portrait video, text overlay of the ask, cut to gameplay. Cheapest reach you'll get; post 1/day for 2 weeks. |
| **Discord servers** | AI art/AI dev servers, itch.io, game jam servers. Only where there's a #showcase or #self-promo channel. |
| **itch.io** | Upload 2–3 of the best built games as free games with "made with GameSummoner" + link. Itch is the exact audience. |
| **r/webgames, r/playmygame, r/WebGames** | Post the games themselves, not the tool. Link back. |
| **Bluesky / Mastodon** | Small, but the indie-dev crowd moved there. Same thread as X. |

### Tier 3 — ongoing

| Where | Notes |
|---|---|
| **Hacker News (again)** | A "what I learned" writeup 2–4 weeks after launch (the measured laws from CLAUDE.md are a great blog post: gates detect broken not bad, first done is answered not accepted, etc.). |
| **Dev blog / docs/experiments.md as posts** | Each experiment is a post. Steady SEO. |
| **YouTube long-form** | One 8–12 min "how it works" video. |
| **Newsletters** | TLDR AI, Ben's Bites, The Rundown accept submissions. Game dev: Game Developer, IndieDB. |
| **Game jams** | Sponsor/enter a jam with "GameSummoner allowed" — this is the community that'll stick. |

### Skip for now

Paid ads (no funnel data yet to optimise), press outreach (need traction numbers first), LinkedIn
(wrong crowd).

---

## 3. What to post

### The one-paragraph pitch (adjust, keep honest)

> Describe a game in a sentence, get a real playable browser game a few minutes later — plain
> HTML/JS, with its own generated art. It runs on an open-weight model on a single rented GPU.
> It makes any KIND of game; whether it's a GOOD game is the part we're still working on, and
> I'd rather show you than tell you: [demo link].

### Rules that hold across every channel

1. **Show the game, not the UI.** Video/screenshots of gameplay. Nobody cares about the create form.
2. **Lead with the ask.** The hook is always "I typed THIS → got THIS". The ask text is in the image.
3. **Honesty is the differentiator.** "Sometimes it makes a bad game. Here's one." disarms the
   AI-slop reply before it's written. You have a doctrine of not faking quality; say so.
4. **Price up front.** Credits start at 0 with no free play — say what one game costs in the post
   or the first reply is "paywall".
5. **Reply to everything for the first 48 h.** The comments ARE the launch.
6. **One absurd ask per post.** "A tower defense where the towers are anxious cats" beats "a
   platformer". Absurd asks are shareable and prove "any game".
7. **Never argue with "AI art is theft" threads.** Acknowledge once, move on.

### Per-channel drafts

**Show HN title options**
- `Show HN: GameSummoner – type a game idea, get a playable browser game (Qwen on one GPU)`
- `Show HN: I built a service where an open-weight model writes whole browser games from a sentence`

**Show HN first comment (skeleton)**
- What it is, one line. Link.
- How: two stages (design → build). No engine, no framework; model writes plain HTML/JS with 8 tools.
- The three things that surprised me (pick from CLAUDE.md: interface-first pipeline lost to
  no-contract 4/4; gates may detect broken not bad; the first `done` is answered not accepted).
- What's bad: honest list. "Good" is the constraint we bend.
- Cost/pricing, and why credits start at 0.
- Ask: "tell me the game you asked for and whether it delivered".

**Reddit (IndieGaming / webgames) post**
- Title: `I asked an AI for "[absurd ask]" and it made this` + video.
- Body: 2 lines, link, price line, "roast it".

**r/LocalLLaMA post**
- Title: `Qwen3.8 Flash-Next on one RTX PRO 6000 writes complete browser games — what I measured`
- Body: model, quant/serving stack, tok/s, context, thinking-on vs off finding, the transcript-is-
  memory approach, what failed. Link at the bottom, not the top.

**X thread**
1. Video. "I built a thing: describe a game, get a game. Thread ↓"
2–6. One screenshot each, ask text as the tweet.
7. "How it works" — 3 lines.
8. "It's not always good. Here's a bad one." + link.
9. Link + price.

**Product Hunt**
- Tagline (≤60 chars): `Describe a game. Play it minutes later.`
- Maker comment = the HN first comment, shorter.

**Short-form video script (15–30 s)**
- 0–3 s: text overlay of the ask being typed.
- 3–5 s: "summoning…" cut.
- 5–25 s: gameplay, no talking, one caption: "made by AI from that one sentence".
- Last 3 s: `gamesummoner.com`.

---

## 4. Launch day sequence

1. Morning: deploy is stable, no pending changes, monitors green, RunPod balance topped up.
2. Post HN (Show HN) + X thread within 10 min of each other.
3. Sit in the HN thread. Reply to every comment in <15 min.
4. Watch: `/api/events/landing` referrers, sign-ups, purchases, builds started vs finished, llm queue depth.
5. Evening: Reddit (one sub). Next day: another sub, PH the day after.
6. Every failed build that day: read it. Write down the ask. That's the roadmap.

## 5. After

- Day 3: write up numbers (visits by referrer → sign-ups → purchases → builds → played) and what
  each channel returned. Decide where to keep posting from data, not vibes.
- Week 2: the "what I learned" post.

---

## 6. Post drafts (OPEN — work session 2026-09-04)

One block per channel. Each block: audience, hook, assets needed, draft, status. Nothing below is
final. Order = order we'll write them.

### 6.1 r/LocalLLaMA — technical writeup
- **Audience:** people running open models locally; care about serving stack, numbers, prompts.
- **Hook:** Qwen3.8 Flash-Next on one RTX PRO 6000 writes complete browser games. Measurements.
- **Assets:** 2–3 gameplay gifs, one build-transcript excerpt, tok/s + boot numbers, cost/game.
- **Draft:** (Nick has plan; paste here)
- **Decide:** how much of design.txt / build.txt to show. What model/serving details are public.
- **Status:** open

### 6.2 Show HN
- **Audience:** engineers/founders. Technical honesty. Will try it within 30 s of reading.
- **Hook:** "Describe a game, get a playable browser game. Open-weight model, one GPU, no engine."
- **Assets:** landing with OG image live, 5 demos loading fast, price on landing.
- **Title:**
- **First comment (what / how / surprised me / what's bad / price / ask):**
- **No-signup story (first comment, line 2):** "demos and every public game need no account; code
  HN = free first build for the first N."
- **Prepared answers:** "why not Claude/GPT?", "is it just a wrapper?", "AI slop", "show a bad one",
  "why credits from 0?", "can I self-host?", "what model?"
- **Status:** open

### 6.3 X / Bluesky thread
- **Audience:** AI builders, indie devs.
- **Hook:** video first tweet.
- **Assets:** 30–60 s landscape video; 5 screenshots with ask text baked in.
- **Tweets 1–9:**
- **Status:** open

### 6.4 r/IndieGaming + r/webgames + r/playmygame
- **Audience:** players and hobby devs. Post the GAME, not the tool.
- **Hook:** "I asked an AI for [absurd ask] and it made this" + video.
- **Assets:** 2 absurd-ask games, playable via public link (needs share URL — §1).
- **Title / body:**
- **Status:** open, blocked on share URL

### 6.5 Product Hunt
- **Assets:** tagline, 5 gallery images, OG image, maker comment, 10 friends for real comments.
- **Tagline:**
- **Maker comment:**
- **Launch date:**
- **Status:** open

### 6.6 Short-form video (TikTok / Shorts / Reels)
- **Format:** ask typed → cut → gameplay → url. 15–30 s portrait. 1/day × 14.
- **Ask list (14 absurd asks):**
- **Recording setup:**
- **Status:** open

### 6.7 itch.io
- **Assets:** 3 best games as free uploads, page text with link.
- **Which games:**
- **Status:** open

### 6.8 Discord servers
- **Which servers / channels (need #showcase or #self-promo):**
- **One-paragraph blurb + video:**
- **Status:** open

### 6.9 Newsletters (TLDR AI, Ben's Bites, The Rundown)
- **Submission blurb (2 sentences):**
- **Status:** open

### 6.10 Follow-up: "what I learned" post (HN + blog, week 2)
- **Outline:** the measured laws from CLAUDE.md, one per section, with numbers.
- **Status:** later
