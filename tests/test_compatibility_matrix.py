import json
from pathlib import Path


def test_compatibility_matrix_matches_ci_support() -> None:
    matrix = json.loads(Path("docs/contracts/compatibility-matrix.json").read_text())
    assert matrix["platform_api"] == ["1.1"]
    assert matrix["python"] == ["3.12", "3.13", "3.14"]
    assert all(matrix["support"].values())
    assert len(matrix["security_regressions"]) >= 6
