#!/usr/bin/env python3
"""Code formatting script using black and isort."""

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
        print(f"❌ {description} failed with exit code {result.returncode}")
        return False

    print(f"✅ {description} completed successfully")
    return True


def run_format(check_only: bool = False) -> int:
    """
    Run code formatting with black and isort.

    Args:
        check_only: If True, only check formatting without making changes

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"

    # Find Python files to format
    py_files = list(backend_dir.rglob("*.py"))
    py_files.extend(project_root.glob("*.py"))

    if not py_files:
        print("No Python files found to format")
        return 0

    print(f"Found {len(py_files)} Python files to process")

    # Prepare commands
    black_cmd = ["uv", "run", "black"]
    isort_cmd = ["uv", "run", "isort"]

    if check_only:
        black_cmd.extend(["--check", "--diff"])
        isort_cmd.extend(["--check", "--diff"])

    black_cmd.extend([str(p) for p in py_files])
    isort_cmd.extend([str(p) for p in py_files])

    # Run formatters
    success = True

    if not run_command(black_cmd, "Black code formatter"):
        success = False

    if not run_command(isort_cmd, "isort import organizer"):
        success = False

    if success:
        print("\n" + "="*60)
        print("✅ All formatting checks passed!")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("❌ Formatting issues found")
        print("="*60)
        if check_only:
            print("\nRun 'uv run script format' to fix formatting issues automatically")

    return 0 if success else 1


def main() -> int:
    """Main entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == "--check":
        return run_format(check_only=True)
    return run_format(check_only=False)


if __name__ == "__main__":
    sys.exit(main())
