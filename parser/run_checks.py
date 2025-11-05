#!/usr/bin/env python3
import sys


def check_if_in_env() -> None:
    if sys.prefix == sys.base_prefix:
        print("❌ Please activate your virtual environment first!")
        print("   (e.g., 'source venv/bin/activate' or 'venv\\Scripts\\activate')")
        sys.exit(1)


check_if_in_env()

import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def run(cmd: list[str], **kwargs: Any) -> None:
    print(f"🔹 Running: {' '.join(cmd)}")
    subprocess.check_call(cmd, **kwargs)


def main() -> None:
    black_cmd = ["black", "."]
    mypy_cmd = ["mypy", "."]

    try:
        run(black_cmd)
        run(mypy_cmd)
    except subprocess.CalledProcessError as e:
        print(f"[ERR] Command failed: {e}")
        sys.exit(e.returncode)

    print("✅ All checks passed!")


if __name__ == "__main__":
    main()
