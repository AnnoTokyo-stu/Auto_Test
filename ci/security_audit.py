"""Fail CI when forbidden runtime files or high-confidence secrets are tracked."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_DIRECTORIES = {
    ".idea",
    ".venv",
    ".venv-ci",
    "__pycache__",
    "node_modules",
    "outputs",
    "tmp",
}
RUNTIME_DIRECTORIES = {
    "log",
    "report",
    "report-html",
    "screenshots",
    "downloads",
    "test_materials",
    "artifacts",
}
ALLOWED_RUNTIME_FILES = {
    "log/.gitkeep",
    "report/.gitkeep",
    "report-html/.gitkeep",
    "screenshots/.gitkeep",
    "downloads/.gitkeep",
    "test_materials/README.md",
}
ALLOWED_ENV_TEMPLATES = {".env.example", ".env.local.example"}
FORBIDDEN_SUFFIXES = {".key", ".pem", ".p12", ".pfx"}
TEXT_SUFFIXES = {
    "",
    ".example",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}

SECRET_PATTERNS = {
    "private key": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "GitHub token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "AWS access key": re.compile(r"\b(?:AKIA|ASIA)[A-Z0-9]{16}\b"),
    "JWT": re.compile(
        r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\."
        r"[A-Za-z0-9_-]{10,}\b"
    ),
    "credential in URL": re.compile(
        r"https?://[^\s/:@]+:[^\s/@]+@[^\s]+", re.IGNORECASE
    ),
}


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [ROOT / item for item in result.stdout.decode("utf-8").split("\0") if item]


def main() -> int:
    violations: list[tuple[str, str]] = []

    for path in tracked_files():
        relative = path.relative_to(ROOT).as_posix()
        parts = set(path.relative_to(ROOT).parts)

        if parts & FORBIDDEN_DIRECTORIES:
            violations.append((relative, "generated or local-only directory"))
            continue

        if path.relative_to(ROOT).parts[0] in RUNTIME_DIRECTORIES:
            if relative not in ALLOWED_RUNTIME_FILES:
                violations.append((relative, "runtime artifact"))
                continue

        if path.name.startswith(".env") and path.name not in ALLOWED_ENV_TEMPLATES:
            violations.append((relative, "environment secret file"))
            continue

        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            violations.append((relative, "private credential file"))
            continue

        if path.suffix.lower() not in TEXT_SUFFIXES or not path.is_file():
            continue

        if path.stat().st_size > 2 * 1024 * 1024:
            continue

        content = path.read_text(encoding="utf-8", errors="ignore")
        for rule, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                violations.append((relative, rule))

    if violations:
        print("CI security audit failed:")
        for relative, rule in sorted(set(violations)):
            print(f"- {relative}: {rule}")
        return 1

    print("CI security audit passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
