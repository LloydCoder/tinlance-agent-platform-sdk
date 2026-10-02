"""Safe local diagnostics for the Tinlance Agent Platform SDK."""

from __future__ import annotations

import json
import platform
import sys

from .compat import PLATFORM_API_VERSION, SDK_VERSION


def diagnostics() -> dict[str, str]:
    """Return non-secret environment and SDK compatibility diagnostics."""
    return {
        "sdk_version": SDK_VERSION,
        "platform_api_version": PLATFORM_API_VERSION,
        "python": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "supported_python": ">=3.12,<3.15",
    }


def main() -> None:
    """Print diagnostics without reading credentials or making network calls."""
    json.dump(diagnostics(), sys.stdout, sort_keys=True)
    sys.stdout.write("\n")
