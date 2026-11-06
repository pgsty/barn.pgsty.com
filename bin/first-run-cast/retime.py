#!/usr/bin/env python3
"""Retime an asciicast v2 recording without changing any output bytes.

- Every gap between events is capped at --max-gap seconds.
- Each --squeeze START:END:SECONDS window (START/END are substrings of the
  output stream; END is searched after START) is rescaled so that the
  events between them span at most SECONDS. Use it for long progress bars
  and boot waits.
"""
import argparse
import json
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("src")
    parser.add_argument("dst")
    parser.add_argument("--max-gap", type=float, default=1.4)
    parser.add_argument("--squeeze", action="append", default=[])
    parser.add_argument("--title")
    args = parser.parse_args()

    with open(args.src, encoding="utf-8") as handle:
        header = json.loads(handle.readline())
        events = [json.loads(line) for line in handle if line.strip()]

    outputs = [e for e in events if e[1] == "o"]
    times = [e[0] for e in outputs]
    gaps = [times[0]] + [b - a for a, b in zip(times, times[1:])]

    # Locate squeeze windows by output substrings (on the cumulative stream).
    stream, offsets = "", []
    for event in outputs:
        offsets.append(len(stream))
        stream += event[2]

    def index_at(char_pos):
        lo, hi = 0, len(offsets) - 1
        while lo < hi:
            mid = (lo + hi + 1) // 2
            if offsets[mid] <= char_pos:
                lo = mid
            else:
                hi = mid - 1
        return lo

    scale = [1.0] * len(gaps)
    cursor = 0
    for spec in args.squeeze:
        start, end, seconds = spec.rsplit(":", 2) if spec.count(":") >= 2 else (None, None, None)
        start_pos = stream.find(start, cursor)
        end_pos = stream.find(end, start_pos + len(start)) if start_pos >= 0 else -1
        if start_pos < 0 or end_pos < 0:
            sys.exit(f"squeeze window not found: {spec!r}")
        first, last = index_at(start_pos) + 1, index_at(end_pos)
        span = sum(min(g, args.max_gap) for g in gaps[first:last + 1])
        factor = min(1.0, float(seconds) / span) if span > 0 else 1.0
        for i in range(first, last + 1):
            scale[i] = factor
        print(f"squeeze {start!r}..{end!r}: {span:.1f}s -> {span * factor:.1f}s", file=sys.stderr)
        cursor = end_pos

    clock, retimed = 0.0, []
    for event, gap, factor in zip(outputs, gaps, scale):
        clock += min(gap, args.max_gap) * factor
        retimed.append([round(clock, 4), "o", event[2]])

    header.pop("idle_time_limit", None)
    if args.title:
        header["title"] = args.title
    header.pop("env", None)
    header.pop("command", None)
    with open(args.dst, "w", encoding="utf-8") as handle:
        handle.write(json.dumps(header, ensure_ascii=False) + "\n")
        for event in retimed:
            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
    print(f"{len(retimed)} events, {times[-1]:.1f}s -> {clock:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
