import json
from pathlib import Path


def test_m21_6_security_matrix_is_complete_and_executable() -> None:
    matrix = json.loads(Path("docs/security/m21-6-control-matrix.json").read_text(encoding="utf-8"))
    controls = matrix["controls"]
    assert len(controls) >= 14
    assert all(item["status"] == "verified" for item in controls)
    assert all(item["verification"] for item in controls)
    required = {
        "credential isolation",
        "tenant and principal binding",
        "approval fail-closed boundary",
        "telemetry payload minimization",
        "dependency audit and SBOM",
        "artifact provenance",
        "CodeQL static analysis",
        "contract drift detection",
    }
    assert required.issubset({item["control"] for item in controls})


def test_m21_6_release_requirements_are_non_empty() -> None:
    matrix = json.loads(
        Path("docs/security/m21-6-control-matrix.json").read_text(encoding="utf-8")
    )
    assert len(matrix["release_requirements"]) >= 6
