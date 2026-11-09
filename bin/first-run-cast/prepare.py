#!/usr/bin/env python3
"""Prepare the macOS take for retiming; keep the original recording separately.

Omit this host's unrelated mtplx tap diagnostic and the final shell exit.
Repair the beer emoji misdecoded by macOS Expect. Barn output is untouched.
"""
import json
import re
import sys


def main(src, dst):
    with open(src, encoding="utf-8") as handle:
        header = json.loads(handle.readline())
        events = [json.loads(line) for line in handle if line.strip()]
    stream = "".join(e[2] for e in events if e[1] == "o")
    cuts = []
    warning = re.search(
        r"Warning: The following taps are not trusted:\r*\n"
        r"  youssofal/mtplx\r*\n\r*\n"
        r"Homebrew is currently ignoring formulae, casks and commands.*?"
        r"  https://docs\.brew\.sh/Tap-Trust\r*\n\r*\n",
        stream, re.DOTALL,
    )
    if warning:
        cuts.append(warning.span())
    end = re.search(r"exit\r*\n$", stream)
    if end:
        cuts.append(end.span())

    position = 0
    for event in events:
        if event[1] != "o":
            continue
        original = event[2]
        # Apply stream offsets even when a cut crosses event boundaries.
        for start, stop in reversed(cuts):
            left, right = max(start - position, 0), min(stop - position, len(original))
            if left < right:
                event[2] = event[2][:left] + event[2][right:]
        position += len(original)
        event[2] = event[2].replace("\u00f0\u009f\u008d\u00ba", "🍺")

    with open(dst, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(header, ensure_ascii=False) + "\n")
        for event in events:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(f"Omitted {len(cuts)} presentation-only spans; retained all Barn output.")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
