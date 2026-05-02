"""Entry point for `python -m scythe_honeypot`."""

import sys

# Force UTF-8 sur la console Windows AVANT d'importer Textual
if sys.platform == "win32":
    import os
    os.system("")  # active les escape codes ANSI sur cmd.exe
    # Force la codepage UTF-8
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        ctypes.windll.kernel32.SetConsoleCP(65001)
    except Exception:
        pass
    # Force les flux Python en UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from scythe_honeypot.app import main

if __name__ == "__main__":
    main()