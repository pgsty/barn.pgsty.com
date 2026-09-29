#!/usr/bin/env python3
"""Check internal HTML links, assets, and fragments in a built Hugo site."""

from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: set[str] = set()
        self.references: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        if tag in {"a", "area", "link"} and values.get("href"):
            self.references.append(values["href"] or "")
        if tag in {"audio", "iframe", "img", "script", "source", "video"} and values.get("src"):
            self.references.append(values["src"] or "")
        if tag in {"img", "source"} and values.get("srcset"):
            for candidate in (values["srcset"] or "").split(","):
                reference = candidate.strip().split(maxsplit=1)[0]
                if reference:
                    self.references.append(reference)


def public_url(path: Path, root: Path) -> str:
    rel = path.relative_to(root).as_posix()
    if rel == "index.html":
        return "/"
    if rel.endswith("/index.html"):
        return "/" + rel[: -len("index.html")]
    return "/" + rel


def target_file(path: str, root: Path) -> Path | None:
    clean = unquote(path).lstrip("/")
    candidate = root / clean
    choices = [candidate]
    if path.endswith("/") or not candidate.suffix:
        choices.append(candidate / "index.html")
    if candidate.suffix == ".html":
        choices.append(candidate)
    for choice in choices:
        if choice.is_file():
            return choice
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    args = parser.parse_args()
    root = args.root.resolve()
    pages: dict[Path, PageParser] = {}

    for path in sorted(root.rglob("*.html")):
        parsed = PageParser()
        parsed.feed(path.read_text(encoding="utf-8", errors="replace"))
        pages[path.resolve()] = parsed

    errors: list[str] = []
    for source, parsed in pages.items():
        source_url = public_url(source, root)
        # Oink's section-print output concatenates child articles into one
        # document. Their original page-relative links are meaningful in the
        # interactive pages and intentionally not a second print URL graph.
        if "/_print/" in source_url or source_url.startswith("/_print/"):
            continue
        base_url = "https://barn.pgsty.com" + source_url
        for raw in parsed.references:
            split = urlsplit(raw)
            if split.scheme in {"mailto", "tel", "javascript", "data"}:
                continue
            if split.netloc and split.netloc != "barn.pgsty.com":
                continue
            absolute = urlsplit(urljoin(base_url, raw))
            target = target_file(absolute.path, root)
            if target is None:
                errors.append(f"{source_url}: missing {raw}")
                continue
            if absolute.fragment and target.suffix == ".html":
                target_parser = pages.get(target.resolve())
                if target_parser is None:
                    target_parser = PageParser()
                    target_parser.feed(target.read_text(encoding="utf-8", errors="replace"))
                    pages[target.resolve()] = target_parser
                fragment = unquote(absolute.fragment)
                if fragment not in target_parser.ids:
                    errors.append(f"{source_url}: missing fragment {raw}")

    if errors:
        for error in errors:
            print(error)
        print(f"internal link check failed: {len(errors)} error(s)")
        return 1

    print(f"internal link and asset check passed: {len(pages)} HTML page(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
