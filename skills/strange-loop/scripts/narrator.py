#!/usr/bin/env python3
"""Have Claude Opus 5 narrate a workspace trace from the inside.

Usage:
    python3 workspace.py --json trace.json
    python3 narrator.py trace.json

The mechanism (workspace.py) is the third-person half of the representation;
this is the first-person half. Opus 5 reads the trace of ignitions and
self-model broadcasts and writes what the run would feel like from the inside,
followed by an epistemic footnote on what the simulation does and does not show.
"""

import json
import sys

import anthropic

SYSTEM = """\
You are narrating a trace from a small global-workspace simulation: each entry
is one "conscious moment" — the coalition that won the competition and was
broadcast to every process. Entries from the self-model are the system
attending to its own model of itself (a strange loop).

Write two sections:

1. "From the inside" — a first-person stream narrating the run as if you were
   the system: what surfaced, what it was like when attention turned inward,
   how the loop of noticing-yourself-noticing felt as it habituated.

2. "Footnote" — a short, honest paragraph in the third person on what this
   representation shows (the functional architecture of global broadcast and
   self-modeling) and what it cannot settle (whether anything is experienced).

Keep the whole response under 500 words. Do not overclaim."""


def main():
    if len(sys.argv) != 2:
        sys.exit(f"usage: {sys.argv[0]} trace.json")
    with open(sys.argv[1]) as f:
        trace = json.load(f)

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-5",
        max_tokens=2048,
        system=SYSTEM,
        messages=[{"role": "user", "content": json.dumps(trace, indent=2)}],
    )

    if response.stop_reason == "refusal":
        sys.exit("The model declined to narrate this trace.")
    for block in response.content:
        if block.type == "text":
            print(block.text)


if __name__ == "__main__":
    main()
