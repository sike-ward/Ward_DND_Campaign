import sys
import traceback

from Ward_DND_AI.config.config import Config, log_exception
from Ward_DND_AI.gui.gui import LoreMainApp


def handle_crash(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))

    log_exception("UNHANDLED CRASH", error_msg)
    print("An unexpected error occurred. See app.log for details.")
    try:
        import tkinter as tk
        from tkinter import messagebox

        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Crash!", "An unexpected error occurred.\nSee app.log for details."
        )
        root.destroy()
    except Exception:
        pass


Config.setup_logging()
sys.excepthook = handle_crash

if __name__ == "__main__":
    app = LoreMainApp()
    app.mainloop()
