#!/usr/bin/env python3
"""Spread each typed command's echo across the time it was typed.

The driver typed every command character by character, but the local pty
delivered the echo in one burst on Enter. For each output event that starts
with a typed command and follows a prompt, split the command text into
per-character events ending at the original event time. No bytes change.
"""
import json
import sys

TYPED = [
    "curl -fLO https://github.com/pgsty/barn/releases/latest/download/install.sh",
    "bash install.sh",
    'export PATH="$HOME/.local/bin:$PATH"',
    "barn version",
    "barn up",
    "barn ssh",
    "df -h /data",
    "barn status",
    "exit",
    "y",
]
PROMPTS = ("$ ", "[Y/n] ")
STEP = 0.065


def main(src, dst):
    with open(src, encoding="utf-8") as handle:
        header = handle.readline()
        events = [json.loads(line) for line in handle if line.strip()]
    out = []
    for index, event in enumerate(events):
        previous = events[index - 1] if index else None
        text = event[2] if event[1] == "o" else ""
        command = next((c for c in TYPED if text.startswith(c)), None)
        if command and previous and previous[1] == "o" and previous[2].endswith(PROMPTS):
            rest = text[len(command):]
            gap = event[0] - previous[0]
            step = min(STEP, max(gap - 0.4, 0.0) / max(len(command), 1))
            start = event[0] - step * (len(command) - 1)
            for offset, char in enumerate(command):
                piece = char + (rest if offset == len(command) - 1 else "")
                out.append([round(start + step * offset, 6), "o", piece])
            continue
        out.append(event)
    with open(dst, "w", encoding="utf-8") as handle:
        handle.write(header)
        for event in out:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(f"{len(events)} -> {len(out)} events", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
