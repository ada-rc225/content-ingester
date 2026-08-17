#!/usr/bin/env python3
"""Create a condition-blind RQ1 evaluation bundle and a separate secret mapping."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path


HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_sample(value: str) -> tuple[str, str, Path]:
    if "=" not in value:
        raise argparse.ArgumentTypeError("sample must be CONDITION::RUN=PATH")
    identity, raw_path = value.split("=", 1)
    if "::" not in identity:
        raise argparse.ArgumentTypeError("sample must separate condition and run with ::")
    condition, run_id = identity.split("::", 1)
    if not condition.strip() or not run_id.strip() or not raw_path.strip():
        raise argparse.ArgumentTypeError("sample condition, run, and path must be non-empty")
    return condition.strip(), run_id.strip(), Path(raw_path).expanduser().resolve()


def sanitise_markdown(text: str) -> str:
    """Remove hidden generation markers that could reveal the treatment condition."""
    text = HTML_COMMENT.sub("", text)
    lines = [line.rstrip() for line in text.splitlines()]
    return "\n".join(lines).strip() + "\n"


def is_within(child: Path, parent: Path) -> bool:
    try:
        child.relative_to(parent)
        return True
    except ValueError:
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle-id", required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--learner-profile", type=Path, required=True)
    parser.add_argument("--task-brief", type=Path, required=True)
    parser.add_argument("--sample", action="append", type=parse_sample, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--mapping-output", type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    args = parser.parse_args()

    contract_path = args.contract.resolve()
    profile_path = args.learner_profile.resolve()
    task_path = args.task_brief.resolve()
    output_dir = args.output_dir.resolve()
    mapping_path = args.mapping_output.resolve()

    for path, label in ((contract_path, "contract"), (profile_path, "learner profile"), (task_path, "task brief")):
        if not path.is_file():
            parser.error(f"{label} is missing: {path}")
    if output_dir.exists():
        parser.error(f"output directory already exists: {output_dir}")
    if mapping_path.exists():
        parser.error(f"mapping output already exists: {mapping_path}")
    if is_within(mapping_path, output_dir):
        parser.error("mapping output must be outside the blind bundle")

    identities = [(condition, run_id) for condition, run_id, _ in args.sample]
    paths = [path for _, _, path in args.sample]
    if len(set(identities)) != len(identities):
        parser.error("condition/run identities must be unique")
    if len(set(paths)) != len(paths):
        parser.error("sample paths must be unique")
    for path in paths:
        if not path.is_file():
            parser.error(f"sample is missing: {path}")

    contract = json.loads(contract_path.read_text(encoding="utf-8"))
    if contract.get("lifecycle_status") != "frozen" or not contract.get("approval"):
        parser.error("contract must be an approved frozen_reference_contract.json")
    profile = json.loads(profile_path.read_text(encoding="utf-8"))
    if not isinstance(profile, dict):
        parser.error("learner profile must be a JSON object")

    shuffled = list(args.sample)
    random.Random(args.seed).shuffle(shuffled)

    output_dir.mkdir(parents=True)
    samples_dir = output_dir / "samples"
    samples_dir.mkdir()
    shutil.copyfile(contract_path, output_dir / "frozen_reference_contract.json")
    shutil.copyfile(profile_path, output_dir / "learner_profile.json")
    shutil.copyfile(task_path, output_dir / "task_brief.txt")

    public_samples = []
    secret_samples = []
    for index, (condition, run_id, source_path) in enumerate(shuffled, start=1):
        sample_id = f"S{index:03d}"
        original_bytes = source_path.read_bytes()
        prepared_text = sanitise_markdown(original_bytes.decode("utf-8"))
        prepared_path = samples_dir / f"{sample_id}.md"
        prepared_path.write_text(prepared_text, encoding="utf-8")
        public_samples.append({
            "sample_id": sample_id,
            "file": f"samples/{sample_id}.md",
            "content_sha256": sha256_file(prepared_path),
        })
        secret_samples.append({
            "sample_id": sample_id,
            "condition_label": condition,
            "source_run_id": run_id,
            "original_path": str(source_path),
            "original_sha256": sha256_bytes(original_bytes),
            "prepared_sha256": sha256_file(prepared_path),
        })

    manifest = {
        "schema_version": "1.0",
        "evaluation_protocol": "RQ1-EVAL-v1",
        "bundle_id": args.bundle_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "contract": {
            "file": "frozen_reference_contract.json",
            "contract_id": contract["contract_id"],
            "contract_version": contract["contract_version"],
            "sha256": sha256_file(output_dir / "frozen_reference_contract.json"),
        },
        "learner_profile": {
            "file": "learner_profile.json",
            "sha256": sha256_file(output_dir / "learner_profile.json"),
        },
        "task_brief": {
            "file": "task_brief.txt",
            "sha256": sha256_file(output_dir / "task_brief.txt"),
        },
        "sanitisation": {"html_comments_removed": True, "trailing_whitespace_removed": True},
        "samples": public_samples,
    }
    write_json(output_dir / "evaluation_manifest.json", manifest)

    mapping_path.parent.mkdir(parents=True, exist_ok=True)
    write_json(mapping_path, {
        "schema_version": "1.0",
        "bundle_id": args.bundle_id,
        "seed": args.seed,
        "bundle_manifest_sha256": sha256_file(output_dir / "evaluation_manifest.json"),
        "samples": secret_samples,
    })
    print(f"Created blind bundle with {len(public_samples)} samples: {output_dir}")
    print(f"Stored condition mapping separately: {mapping_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
