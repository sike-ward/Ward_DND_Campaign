import datetime
import re
import threading
import tkinter as tk
from tkinter import END, messagebox

import customtkinter as ctk

from Ward_DND_AI.config.config import log_exception
from Ward_DND_AI.utils import (
    auto_link_notes,
    get_all_folders,
    get_note_names,
    make_title_case_filename,
)


class AskController:
    """
    Controller for the Ask AI tab. Handles user prompts, AI queries,
    saving responses, splitting & saving, and clearing history.
    """

    def __init__(self, view, ai, storage, config, status_var=None):
        self.view = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or tk.StringVar()

        self.history = []
        self.last_answer = ""
        self.session_tokens = 0

        # Bind UI events
        self.view.ask_btn.configure(command=self.on_ask)
        self.view.save_btn.configure(command=self.on_save)
        self.view.split_btn.configure(command=self.on_split)
        self.view.clear_btn.configure(command=self.on_clear)
        self.view.preview_btn.configure(command=self._on_preview)

    def on_ask(self):
        prompt = self.view.prompt_box.get("1.0", END).strip()
        if not prompt:
            self.status_var.set("Please enter a prompt.")
            return

        self.view.save_btn.configure(state="disabled")
        self.view.split_btn.configure(state="disabled")
        self.status_var.set("Thinking...")

        threading.Thread(target=self._run_ai, args=(prompt,), daemon=True).start()

    def _run_ai(self, prompt):
        try:
            answer, p_tokens, r_tokens = self.ai.ask(prompt)
        except Exception as e:
            self.status_var.set(f"AI Error: {e}")
            log_exception("AskController AI query failed", e)
            return

        self.session_tokens += p_tokens + r_tokens
        self.last_answer = answer
        self.history.append((prompt, answer))

        self.view.output_box.configure(state="normal")
        self.view.output_box.delete("1.0", END)
        self.view.output_box.insert("1.0", answer)
        self.view.output_box.configure(state="disabled")

        self.status_var.set(f"Done. Tokens: +{p_tokens}/{r_tokens}")
        self.view.save_btn.configure(state="normal")
        self.view.split_btn.configure(state="normal")

    def on_save(self):
        folders = get_all_folders(self.config.VAULT_PATH)
        folder = self._prompt_choice("Save Answer", "Select folder:", folders)
        if folder is None:
            return

        filename = make_title_case_filename(
            self._prompt_text("Enter file name (no extension):")
        )
        if not filename:
            self.status_var.set("Save cancelled.")
            return

        rel = f"{folder}/{filename}.md" if folder else f"{filename}.md"
        content = f"# {filename}\n\n{self.last_answer}"

        try:
            self.storage.write_note(rel, content)
            self.status_var.set(f"Saved answer to: {rel}")
        except Exception as e:
            messagebox.showerror("Save Failed", f"Could not save note: {e}")
            self.status_var.set("Save error.")
            log_exception("AskController save failed", e)

    def on_split(self):
        if not self.last_answer:
            self.status_var.set("Nothing to split.")
            return

        folders = get_all_folders(self.config.VAULT_PATH)
        dest_folder = self._prompt_choice(
            "Split & Save", "Select folder for split notes:", folders
        )
        if dest_folder is None:
            return

        parts = [
            p
            for p in re.split(r"(?=^# )", self.last_answer, flags=re.MULTILINE)
            if p.strip()
        ]
        existing = get_note_names(self.config.VAULT_PATH)
        count, errors = 0, []

        for chunk in parts:
            try:
                title_line, body = chunk.split("\n", 1)
                heading = title_line.lstrip("# ").strip()
                fname = make_title_case_filename(heading)
                rel = f"{dest_folder}/{fname}.md" if dest_folder else f"{fname}.md"
                note_content = (
                    f"# {heading}\n"
                    f"*Generated on {datetime.datetime.now():%Y-%m-%d %H:%M}*\n\n"
                    f"{auto_link_notes(body.strip(), existing)}"
                )
                self.storage.write_note(rel, note_content)
                count += 1
            except Exception as e:
                errors.append(heading)
                log_exception(f"Split failed for: {heading}", e)

        msg = f"Saved {count} notes." + (
            f" Failed: {', '.join(errors)}" if errors else ""
        )
        messagebox.showinfo("Split & Save", msg)
        self.status_var.set(msg)

    def on_clear(self):
        self.history.clear()
        self.view.prompt_box.delete("1.0", END)
        self.view.output_box.configure(state="normal")
        self.view.output_box.delete("1.0", END)
        self.view.output_box.configure(state="disabled")
        self.status_var.set("History cleared.")
        self.view.save_btn.configure(state="disabled")
        self.view.split_btn.configure(state="disabled")

    def _prompt_choice(self, title, label, options):
        dlg = ctk.CTkToplevel()
        dlg.title(title)
        dlg.geometry("360x120")
        ctk.CTkLabel(dlg, text=label).pack(pady=(10, 4))
        var = tk.StringVar(dlg)
        var.set(options[0] if options else "")
        menu = ctk.CTkOptionMenu(dlg, variable=var, values=options)
        menu.pack(pady=4)
        result = {"choice": None}

        def on_ok():
            result["choice"] = var.get()
            dlg.destroy()

        btn = ctk.CTkButton(dlg, text="OK", command=on_ok)
        btn.pack(pady=10)
        dlg.grab_set()
        dlg.wait_window()
        return result["choice"]

    def _prompt_text(self, prompt):
        return tk.simpledialog.askstring("Input", prompt) or ""

    def _on_preview(self):
        text = self.view.output_box.get("1.0", tk.END)
        self.view.output_box.winfo_toplevel().open_preview_window(text)
