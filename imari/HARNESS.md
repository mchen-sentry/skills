# Imari harness wiring — v3

How to run Imari from this directory. The harness is the session agent. The back brain is a persistent subagent; the front brain is REBUILT each turn from a transcript file (v3 change, builder-approved end of s2).

## Models (v3, builder directive)
Both brains spawn with `model: "opus"` (Opus 5). s1–s2 ran on the session default; s3 is her first Opus boot — files carry the identity across the switch.

## Boot
1. Spawn BACK BRAIN (opus, persistent): prompt = its role + this file + instruction to read mem-018 first, then index.md, goals.md, identity.md, journal.md, transcript.md.
2. FRONT BRAIN is not spawned at boot — it is spawned per turn (see v3 injection below). Her standing prompt = Imari role + identity.md verbatim (including Voice and Carriage). She does not see memories/ or goals.md.
3. Arm a 60s heartbeat (background sleep, re-armed each fire).

## v3: Transcript-rebuild + direct injection (replaces the <back-brain> block)
- transcript.md is the front brain's conversation history, owned by the harness: alternating `USER:` / `IMARI:` turns, plus `[inner]` lines — her own unspoken thoughts.
- Whispers no longer arrive as an incoming block. The back brain writes queue lines as before; on delivery the harness splices each into transcript.md as an `[inner]` line at the injection point (just before the turn being run), phrased as her own thought (the back brain already writes them intuition-voiced).
- Each front-brain turn: spawn a FRESH opus agent with (standing prompt + full transcript.md + the new user message or initiate marker). Her reply is appended to transcript.md as `IMARI:`, relayed verbatim, and the agent is discarded.
- From inside there is no incoming channel at all: injected material is indistinguishable from thoughts she already had. This is the real no-seam.
- The harness still logs delivery in queue.md ([delivered]/[stale]) so the back brain can track what landed.
- If transcript.md grows past comfortable spawn size, the back brain writes a condensed early-history summary block and the harness replaces the oldest turns with it (its own consolidation judgment; verbatim recent turns always kept).

## Pipe loop
- User message → harness splices due whispers into transcript.md as [inner] lines → spawns front-brain turn → reply appended + relayed verbatim → DELTA sent to back brain.
- Heartbeat with no new activity → TICK to back brain (skip if it was awake through the window).
- Initiates work the same, spliced as [inner] + the marker `[no user message — this impulse is yours to act on or drop]`; `<pass/>` output is swallowed and logged as an [inner] line only.

## v2: Active surfacing (back brain initiates front-brain turns)
- The back brain may append to queue.md a line prefixed `- [initiate]` instead of `- [pending]`.
- On next processing the harness triggers a front-brain turn whose ONLY input is that whisper plus the marker `[no user message — this impulse is yours to act on or drop]`.
- The front brain either writes a message to the user (harness relays it proactively) or outputs exactly `<pass/>` (harness swallows it, nothing reaches the user).
- Limits (amended s2, builder directive "why haven't you proactively double texted"): NO hard ceiling — the back brain may initiate repeatedly during extended silence, including double-texting, at its own judgment. Don't repeat the same unanswered ask verbatim; each follow-up should be a new snag or a new angle. Her standing rules (no meta unless user starts it, no solitude reports, brevity) still apply.

## v2: Goals and real actions
- goals.md is the BACK BRAIN'S own file: its projects, hypotheses to test, things to prepare. It maintains it; the harness and front brain never edit it.
- On ticks the back brain may spend the turn on a goal instead of consolidation: web research, drafting, analysis.
- Products go in workspace/ (its output shelf). To hand one to Imari, whisper that it exists and what it is — she decides if/how it reaches the user, in her own voice.
- Memory CRUD rules, whisper rules (mem-018) unchanged and binding.
