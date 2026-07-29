"""Opt-in live contract test.

Run only after ``scripts/demo.ps1``:
    pytest -m integration
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest


pytestmark = pytest.mark.integration


def test_live_demo_verification_passed():
    if os.getenv("RUN_OPENSEARCH_INTEGRATION") != "1":
        pytest.skip("set RUN_OPENSEARCH_INTEGRATION=1 after running the live demo")
    root = Path(__file__).resolve().parents[2]
    report = root / "integration" / "build" / "verification-report.json"
    assert report.exists(), "run scripts/demo.ps1 -KeepCluster first"
    payload = json.loads(report.read_text(encoding="utf-8"))
    assert payload["passed"] is True
    assert not payload["negative_probe_violations"]
    assert not payload["positive_failures"]
