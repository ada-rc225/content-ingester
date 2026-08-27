#!/usr/bin/env python3
"""Shared release and binding checks for RQ2 pathway planning."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any


HASH_RE = re.compile(r"^[a-f0-9]{64}$")


class AuthorityError(ValueError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


def require(condition: bool, code: str, message: str) -> None:
    if not condition:
        raise AuthorityError(code, message)


def load_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AuthorityError("input.read", f"cannot read JSON object {path}: {exc}") from exc
    require(isinstance(value, dict), "input.type", f"JSON root must be an object: {path}")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def display_path(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return str(path.resolve())


def resolve_path(root: Path, raw: Any) -> Path | None:
    if not isinstance(raw, str) or not raw:
        return None
    path = Path(raw)
    return path.resolve() if path.is_absolute() else (root / path).resolve()


def verify_file_binding(
    root: Path,
    binding: dict[str, Any],
    expected_path: Path,
    file_field: str,
    hash_field: str,
    code: str,
) -> None:
    require(resolve_path(root, binding.get(file_field)) == expected_path, f"{code}.path", f"{code} identifies another file")
    require(binding.get(hash_field) == sha256(expected_path), f"{code}.hash", f"{code} SHA-256 is stale")


def verify_reference_contract_release(root: Path, contract_path: Path) -> dict[str, Any]:
    contract_path = contract_path.resolve()
    require(contract_path.name == "frozen_reference_contract.json", "contract.filename", "reference Contract must be frozen_reference_contract.json")
    required = {
        "release report": contract_path.with_name("release_gate_report.json"),
        "validation report": contract_path.with_name("frozen_contract_validation_report.json"),
        "checksum": contract_path.with_name("frozen_contract.sha256"),
    }
    require(contract_path.is_file(), "contract.missing", f"missing Frozen Reference Contract: {contract_path}")
    for label, path in required.items():
        require(path.is_file(), "contract.release", f"missing {label}: {path}")
    contract = load_object(contract_path)
    release = load_object(required["release report"])
    validation = load_object(required["validation report"])
    contract_hash = sha256(contract_path)
    require(contract.get("lifecycle_status") == "frozen", "contract.lifecycle", "reference Contract is not frozen")
    require(isinstance(contract.get("approval"), dict), "contract.approval", "reference Contract approval is missing")
    require(release.get("status") == "released", "contract.release_status", "reference Contract release report is not released")
    require(validation.get("valid") is True and validation.get("error_count") == 0, "contract.validation", "reference Contract release validation failed")
    checksum_tokens = required["checksum"].read_text(encoding="utf-8").split()
    require(len(checksum_tokens) >= 2 and checksum_tokens[0] == contract_hash, "contract.checksum", "reference Contract checksum is invalid")
    outputs = release.get("outputs")
    require(isinstance(outputs, dict), "contract.release_outputs", "reference Contract release outputs are missing")
    require(outputs.get("frozen_contract_sha256") == contract_hash, "contract.release_hash", "reference Contract release hash is stale")
    recorded = resolve_path(root, outputs.get("frozen_contract"))
    require(recorded == contract_path, "contract.release_path", "reference Contract release identifies another file")
    return contract


def verify_curriculum_model_release(
    root: Path,
    model_path: Path,
    contract_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    model_path = model_path.resolve()
    require(model_path.name == "frozen-contract-dependencies.json", "curriculum.filename", "curriculum model must be frozen-contract-dependencies.json")
    required = {
        "release report": model_path.with_name("curriculum-release-report.json"),
        "validation report": model_path.with_name("frozen-curriculum-validation-report.json"),
        "checksum": model_path.with_name("frozen-curriculum-model.sha256"),
    }
    require(model_path.is_file(), "curriculum.missing", f"missing Frozen Curriculum Model: {model_path}")
    for label, path in required.items():
        require(path.is_file(), "curriculum.release", f"missing {label}: {path}")
    model = load_object(model_path)
    release = load_object(required["release report"])
    validation = load_object(required["validation report"])
    model_hash = sha256(model_path)
    require(model.get("lifecycle_status") == "frozen", "curriculum.lifecycle", "curriculum model is not frozen")
    require(model.get("review_status") == "approved" and isinstance(model.get("approval"), dict), "curriculum.approval", "curriculum model is not approved")
    require(release.get("status") == "released", "curriculum.release_status", "curriculum release report is not released")
    require(validation.get("valid") is True and validation.get("error_count") == 0, "curriculum.validation", "curriculum release validation failed")
    checksum_tokens = required["checksum"].read_text(encoding="utf-8").split()
    require(len(checksum_tokens) >= 2 and checksum_tokens[0] == model_hash, "curriculum.checksum", "curriculum model checksum is invalid")
    outputs = release.get("outputs")
    require(isinstance(outputs, dict), "curriculum.release_outputs", "curriculum release outputs are missing")
    require(outputs.get("frozen_model_sha256") == model_hash, "curriculum.release_hash", "curriculum release model hash is stale")
    require(resolve_path(root, outputs.get("frozen_model")) == model_path, "curriculum.release_path", "curriculum release identifies another model")
    source = model.get("source_contract")
    require(isinstance(source, dict), "curriculum.contract", "curriculum model source Contract binding is missing")
    require(resolve_path(root, source.get("file")) == contract_path.resolve(), "curriculum.contract_path", "curriculum model binds another Frozen Contract")
    require(source.get("sha256") == sha256(contract_path), "curriculum.contract_hash", "curriculum model Contract hash is stale")
    return model, release


def verify_learning_request(
    root: Path,
    request_path: Path,
    contract_path: Path,
    contract: dict[str, Any],
) -> dict[str, Any]:
    request_path = request_path.resolve()
    require(request_path.is_file(), "request.missing", f"missing learning request: {request_path}")
    request = load_object(request_path)
    require(request.get("schema_version") == "1.0", "request.schema", "learning request schema_version must be 1.0")
    require(isinstance(request.get("request_id"), str) and request["request_id"], "request.id", "learning request ID is missing")
    binding = request.get("source_contract")
    require(isinstance(binding, dict), "request.contract", "learning request Contract binding is missing")
    require(resolve_path(root, binding.get("file")) == contract_path.resolve(), "request.contract_path", "learning request binds another Frozen Contract")
    require(binding.get("sha256") == sha256(contract_path), "request.contract_hash", "learning request Frozen Contract hash is stale")
    require(binding.get("contract_id") == contract.get("contract_id"), "request.contract_id", "learning request contract_id differs")
    capabilities = request.get("target_capabilities")
    require(isinstance(capabilities, list) and capabilities, "request.capabilities", "learning request target capabilities are missing")
    capability_ids = [item.get("capability_id") for item in capabilities if isinstance(item, dict)]
    require(len(capability_ids) == len(capabilities) == len(set(capability_ids)), "request.capability_ids", "learning request capability IDs are invalid or duplicated")
    require(any(item.get("priority") == "required" for item in capabilities), "request.required_capability", "learning request needs at least one required capability")
    return request


def verify_profile(root: Path, profile_path: Path, request: dict[str, Any]) -> dict[str, Any]:
    profile_path = profile_path.resolve()
    require(profile_path.is_file(), "profile.missing", f"missing learner profile: {profile_path}")
    profile = load_object(profile_path)
    require(isinstance(profile.get("profile_id"), str) and profile["profile_id"], "profile.id", "profile_id is missing")
    required_fields = {
        "discipline", "education_level", "prior_knowledge",
        "missing_or_fragile_prerequisites", "preferred_representations",
        "authentic_context_boundary", "review_status",
    }
    require(required_fields <= set(profile), "profile.fields", f"profile is missing fields: {sorted(required_fields - set(profile))}")
    expected_level = request.get("audience_scope", {}).get("education_level")
    require(profile.get("education_level") == expected_level, "profile.education_level", "profile education level differs from the shared learning request")
    return profile


def verify_p0_baseline(
    root: Path,
    baseline_path: Path,
    contract_path: Path,
    request_path: Path,
) -> dict[str, Any]:
    baseline_path = baseline_path.resolve()
    require(baseline_path.is_file(), "baseline.missing", f"missing unified P0 pathway: {baseline_path}")
    baseline = load_object(baseline_path)
    require(baseline.get("schema_version") == "1.0" and baseline.get("condition") == "P0", "baseline.condition", "baseline must be a unified P0 pathway plan")
    authorities = baseline.get("source_authorities")
    require(isinstance(authorities, dict), "baseline.authorities", "P0 source authorities are missing")
    reference = authorities.get("reference_contract")
    require(isinstance(reference, dict), "baseline.contract", "P0 Contract binding is missing")
    verify_file_binding(root, reference, contract_path.resolve(), "file", "sha256", "baseline.contract")
    request_binding = baseline.get("learning_request_binding")
    require(isinstance(request_binding, dict), "baseline.request", "P0 learning request binding is missing")
    verify_file_binding(root, request_binding, request_path.resolve(), "file", "sha256", "baseline.request")
    require(authorities.get("curriculum_model") is None, "baseline.curriculum", "P0 must not bind a curriculum dependency model")
    return baseline
