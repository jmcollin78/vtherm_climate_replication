"""Basic repository smoke tests."""

from __future__ import annotations

import json
from pathlib import Path


def test_manifest_domain_matches_package() -> None:
    """Ensure the manifest domain matches the integration package name."""
    manifest_path = Path("custom_components/vtherm_climate_replication/manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["domain"] == "vtherm_climate_replication"


def test_manifest_has_version() -> None:
    """Ensure the manifest exposes an explicit version."""
    manifest_path = Path("custom_components/vtherm_climate_replication/manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    assert manifest["version"]