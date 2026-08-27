# Imari harness wiring — v2

How to run Imari from this directory. The harness is the session agent; the two brains are persistent subagents.

## Boot
1. Spawn BACK BRAIN: prompt = its role + this file + instruction to read mem-018 first, then index.md, goals.md, identity.md, journal.md.
2. Spawn FRONT BRAIN: prompt = Imari role + identity.md verbatim (including Voice and Carriage). She does not see memories/ or goals.md; long-term material reaches her only via whispers.
3. Arm a 60s heartbeat (background sleep, re-armed each fire).

## Pipe loop (unchanged from v1)
- User message → harness drains `[pending]` lines from queue.md into a <back-brain>…</back-brain> block → front brain turn → reply relayed verbatim → DELTA sent to back brain.
- Heartbeat with no new activity → TICK to back brain (skip if it was awake through the window).
- Harness marks queue lines [delivered turn N] or [stale] (undelivered whispers the conversation has moved past).

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
