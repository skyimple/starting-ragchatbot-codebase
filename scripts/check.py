#!/usr/bin/env python3
"""Code quality check script running flake8 and mypy."""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """Run a command and report success/failure."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    result = subprocess.run(cmd)

    if result.returncode != 0:
        print(f"❌ {description} found issues")
        return False

    print(f"✅ {description} passed")
    return True


def run_check() -> int:
    """
    Run code quality checks with flake8 and mypy.

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"

    # Find Python files to check
    py_files = list(backend_dir.rglob("*.py"))
    py_files.extend(project_root.glob("*.py"))

    if not py_files:
        print("No Python files found to check")
        return 0

    print(f"Found {len(py_files)} Python files to check")

    # Prepare commands
    flake8_cmd = ["uv", "run", "flake8", "--config=pyproject.toml"]
    mypy_cmd = ["uv", "run", "mypy", "--config-file=pyproject.toml"]

    flake8_cmd.extend([str(p) for p in py_files])
    mypy_cmd.extend([str(p) for p in py_files])

    # Run linters
    results = []

    results.append(run_command(flake8_cmd, "flake8 linter"))

    # mypy is optional - continue even if it fails
    mypy_result = run_command(mypy_cmd, "mypy type checker")
    results.append(mypy_result)

    # Summary
    all_passed = all(results)

    print("\n" + "="*60)
    if all_passed:
        print("✅ All quality checks passed!")
    else:
        print("❌ Some quality checks failed")
        print("\nTo fix formatting issues, run:")
        print("  uv run script format")
    print("="*60)

    return 0 if all_passed else 1


def main() -> int:
    """Main entry point."""
    return run_check()


if __name__ == "__main__":
    sys.exit(main())
