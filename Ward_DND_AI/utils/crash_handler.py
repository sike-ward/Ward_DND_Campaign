import os
import platform
import sys
import tkinter as tk
import traceback
from datetime import datetime
from tkinter import messagebox

from Ward_DND_AI.config.config import log_exception

LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)


def handle_crash(exc_type, exc_value, exc_traceback, log_to_file_only=False):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(LOG_DIR, f"crash_{timestamp}.log")
    summary_file = os.path.join(LOG_DIR, "last_crash_summary.txt")

    header = (
        f"Timestamp: {datetime.now().isoformat()}\n"
        f"Platform: {platform.platform()}\n"
        f"Python: {platform.python_version()}\n"
        f"Executable: {sys.executable}\n"
        f"Args: {' '.join(sys.argv)}\n" + "-" * 80 + "\n"
    )

    error_msg = header + "".join(
        traceback.format_exception(exc_type, exc_value, exc_traceback)
    )

    log_exception("UNHANDLED CRASH", error_msg)

    # Save to crash log
    with open(log_file, "w", encoding="utf-8") as f:
        f.write(error_msg)

    # Save summary
    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(f"{exc_type.__name__}: {exc_value}\nSee full log: {log_file}")

    if log_to_file_only:
        return

    print("\n>>> UNHANDLED EXCEPTION:\n")
    print(error_msg)

    try:
        root = tk.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(error_msg)
        root.update()
        messagebox.showerror(
            "App Crash",
            "An error occurred. Full log saved to logs/. Copied to clipboard.",
        )
        root.destroy()
    except Exception as gui_err:
        print("[crash_handler] Failed to show error dialog:", gui_err)


# Auto-hook for any uncaught exception in app
sys.excepthook = lambda etype, val, tb: handle_crash(etype, val, tb)
