import sys
import traceback
from gui import LoreMainApp
from config import log_exception, Config

def handle_crash(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    # Log full traceback to app.log
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_exception("UNHANDLED CRASH", error_msg)
    # Print and (optionally) show a dialog
    print("An unexpected error occurred. See app.log for details.")
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Crash!", "An unexpected error occurred.\nSee app.log for details.")
        root.destroy()
    except Exception:
        pass  # fallback if tkinter is somehow unavailable

Config.setup_logging()
sys.excepthook = handle_crash

if __name__ == "__main__":
    app = LoreMainApp()
    app.mainloop()
