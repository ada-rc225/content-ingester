#!/usr/bin/env python3
"""Build a deterministic SHA-256 manifest for authoritative source files."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


FORMAT_BY_SUFFIX = {
    ".md": "markdown",
    ".markdown": "markdown",
    ".ipynb": "notebook",
    ".pdf": "pdf",
    ".pptx": "pptx",
    ".py": "code",
    ".r": "code",
    ".txt": "text",
}


def slug(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return result or "source"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", action="append", required=True, help="Source file; repeat for multiple files")
    parser.add_argument("--output", required=True, help="Destination source_manifest.json")
    parser.add_argument("--workspace-root", default=".")
    parser.add_argument("--role", choices=["authoritative", "supplementary"], default="authoritative")
    args = parser.parse_args()

    root = Path(args.workspace_root).resolve()
    seen: dict[str, int] = {}
    sources = []
    for raw_path in args.source:
        path = Path(raw_path).resolve()
        if not path.is_file():
            parser.error(f"source does not exist or is not a file: {raw_path}")
        base_id = slug(path.stem)
        seen[base_id] = seen.get(base_id, 0) + 1
        source_id = base_id if seen[base_id] == 1 else f"{base_id}-{seen[base_id]}"
        try:
            recorded_path = str(path.relative_to(root))
        except ValueError:
            recorded_path = str(path)
        sources.append(
            {
                "source_id": source_id,
                "path": recorded_path,
                "format": FORMAT_BY_SUFFIX.get(path.suffix.lower(), "other"),
                "sha256": sha256(path),
                "size_bytes": path.stat().st_size,
                "role": args.role,
            }
        )

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps({"hash_algorithm": "sha256", "sources": sources}, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
