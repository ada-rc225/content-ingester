#!/usr/bin/env python3
"""Execute fenced Python blocks and emit machine-readable results.

Execution uses a temporary working directory and Python isolated mode. This is a
reproducibility check, not a security sandbox; host-level sandboxing remains the
responsibility of the calling environment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path


BLOCK_RE = re.compile(r"```(?:python|py)\s*\n(.*?)```", re.DOTALL | re.IGNORECASE)
ANCHOR_RE = re.compile(r"<!--\s*(claim-GEN-[A-Za-z0-9._-]+)\s*-->")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--content", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=float, default=20.0)
    args = parser.parse_args()

    content_path = Path(args.content).resolve()
    text = content_path.read_text(encoding="utf-8")
    results = []

    for index, match in enumerate(BLOCK_RE.finditer(text), start=1):
        code = match.group(1)
        anchors = list(ANCHOR_RE.finditer(text[: match.start()]))
        anchor = anchors[-1].group(1) if anchors else None
        started = time.monotonic()
        try:
            with tempfile.TemporaryDirectory(prefix="adapter-code-") as temp_dir:
                completed = subprocess.run(
                    [sys.executable, "-I", "-c", code],
                    cwd=temp_dir,
                    capture_output=True,
                    text=True,
                    timeout=args.timeout,
                    check=False,
                )
            status = "passed" if completed.returncode == 0 else "failed"
            stdout, stderr, return_code = completed.stdout, completed.stderr, completed.returncode
        except subprocess.TimeoutExpired as exc:
            status = "timeout"
            stdout = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            stderr = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
            return_code = None
        results.append(
            {
                "block_id": f"CODE-{index:03d}",
                "anchor": anchor,
                "language": "python",
                "code_sha256": hashlib.sha256(code.encode("utf-8")).hexdigest(),
                "execution_status": status,
                "stdout": stdout,
                "stderr": stderr,
                "return_code": return_code,
                "duration_ms": round((time.monotonic() - started) * 1000),
            }
        )

    overall = "no_code" if not results else ("passed" if all(r["execution_status"] == "passed" for r in results) else "failed")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps({"content_file": str(content_path), "overall_status": overall, "blocks": results}, indent=2) + "\n",
        encoding="utf-8",
    )
    return 0 if overall != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
