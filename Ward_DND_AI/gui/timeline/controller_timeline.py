import tkinter as tk
from tkinter import messagebox, simpledialog


class TimelineController:
    def __init__(self, view, ai, storage, config, status_var=None):
        self.view = view
        self.ai = ai
        self.storage = storage
        self.config = config
        self.status_var = status_var or tk.StringVar()

        self.view.add_btn.configure(command=self.add_event)
        self.view.edit_btn.configure(command=self.edit_event)
        self.view.delete_btn.configure(command=self.delete_event)

        self._load_events()

    def _load_events(self):
        # For now, no persistence—start empty
        self.events = []
        self._refresh_listbox()

    def _refresh_listbox(self):
        self.view.event_list.delete(0, "end")
        for ev in self.events:
            self.view.event_list.insert("end", ev)

    def add_event(self):
        text = simpledialog.askstring("New Event", "Event description:")
        if text:
            self.events.append(text)
            self._refresh_listbox()

    def edit_event(self):
        idxs = self.view.event_list.curselection()
        if not idxs:
            return
        idx = idxs[0]
        current = self.events[idx]
        text = simpledialog.askstring(
            "Edit Event", "Event description:", initialvalue=current
        )
        if text:
            self.events[idx] = text
            self._refresh_listbox()

    def delete_event(self):
        idxs = self.view.event_list.curselection()
        if not idxs:
            return
        if messagebox.askyesno("Delete?", "Remove selected event?"):
            idx = idxs[0]
            del self.events[idx]
            self._refresh_listbox()
