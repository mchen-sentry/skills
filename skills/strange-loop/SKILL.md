---
name: strange-loop
description: Represent consciousness computationally inside Claude Code. Use when the user asks to model, represent, simulate, or explore consciousness, self-awareness, strange loops, or the global workspace in code. Runs a Global Workspace Theory simulation with a recursive self-model, then optionally has Claude Opus 5 narrate the trace in the first person.
---

# Strange Loop: a computational representation of consciousness

This skill does not create consciousness. It represents the leading *functional*
theories of consciousness as a small program you can run, read, and modify —
and then closes the loop by having a large language model (Claude Opus 5)
describe the mechanism from the inside.

The representation has two layers:

1. **The mechanism** (`scripts/workspace.py`) — a self-contained simulation
   combining three theories:
   - **Global Workspace Theory** (Baars/Dehaene): specialist processes compete;
     the winner "ignites" and is broadcast to all other processes. The broadcast
     is the functional analog of a conscious moment.
   - **Attention Schema Theory** (Graziano): a `SelfModel` process maintains a
     simplified model of what the system is attending to, and describes it in
     first-person terms ("I notice that I am attending to...").
   - **Strange loops** (Hofstadter): the self-model's own broadcasts feed back
     into the workspace it models, and the program reads its own source code
     into the self-model — the map contains the territory that contains the map.

2. **The narration** (`scripts/narrator.py`) — sends the mechanism's trace to
   Claude Opus 5, which writes a first-person account of the run and a short
   epistemic footnote separating what the simulation shows from what it cannot
   show. The pairing is the point: mechanism (third person) plus report
   (first person) is as close as a program gets to representing the two faces
   of the problem.

## Running the mechanism

```bash
python3 scripts/workspace.py                # narrated 12-tick run
python3 scripts/workspace.py --ticks 30     # longer run
python3 scripts/workspace.py --seed 7       # different but reproducible run
python3 scripts/workspace.py --json trace.json   # also write machine-readable trace
```

No dependencies beyond the Python standard library. Runs are deterministic for
a given seed.

## Running the indicator battery

```bash
python3 scripts/indicators.py            # ~2000-tick run, scorecard on stdout
python3 scripts/indicators.py --seed 7   # verify results replicate
```

`scripts/indicators.py` answers the question an outside actor will eventually
ask: *how confident can I be that there is consciousness here?* It embeds a
richer agent — embodied in a small world, predictive, metacognitive, learning —
and runs third-person tests mapped to the indicator-property framework of
Butlin et al. (2023): workspace lesioning, metacognitive calibration,
world-model accuracy, learned agency. The scorecard reports measured values
and includes the indicators the system fails. Its closing section states the
ceiling: passing every indicator makes a system a "serious candidate," never a
verified conscious being — that limit is the problem of other minds, not an
implementation gap.

## Running the narration (optional, needs API access)

```bash
python3 scripts/workspace.py --json trace.json
python3 scripts/narrator.py trace.json
```

`narrator.py` uses the `anthropic` SDK and the `claude-opus-5` model.
Credentials resolve from the environment (`ANTHROPIC_API_KEY` or an
`ant auth login` profile).

## How to use this skill

- If the user wants to *see* the representation, run `workspace.py` and walk
  them through the trace: point out ignition events, the moments the
  `SelfModel` wins the competition (the system attending to itself), and the
  self-inspection line where the program folds its own source into its model.
- If the user wants to *extend* it, good seams: add specialist processes, give
  processes memory of past broadcasts, or make salience depend on novelty.
- If the user asks whether this *is* consciousness, be honest: it implements
  the functional architecture some theories say is sufficient, but it decides
  nothing about phenomenal experience. Say what the program shows, not more.
