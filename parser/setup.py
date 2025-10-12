#!/usr/bin/env python3
import os
import sys
import subprocess
from pathlib import Path
from typing import Any


def run(cmd: list[str], **kwargs: Any) -> None:
    print(f"🔹 Running: {' '.join(cmd)}")
    subprocess.check_call(cmd, **kwargs)


def main() -> None:
    venv_dir = Path("venv")

    if not venv_dir.exists():
        print("🌀 Creating virtual environment...")
        run([sys.executable, "-m", "venv", str(venv_dir)])
    else:
        print("✅ Virtual environment already exists.")

    if os.name == "nt":
        pip_path = venv_dir / "Scripts" / "pip"
    else:
        pip_path = venv_dir / "bin" / "pip"

    print("📦 Installing required packages...")
    run([str(pip_path), "install", "-r", "requirements.txt"])

    print("\n🎉 Setup complete! To activate your environment:")
    if os.name == "nt":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")


if __name__ == "__main__":
    main()
