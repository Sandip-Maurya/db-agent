from __future__ import annotations

import subprocess
import sys


def main() -> int:
    cmd = [sys.executable, "-m", "streamlit", "run", "streamlit_app/app.py"]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
