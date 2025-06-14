import tkinter as tk

import customtkinter as ctk

from Ward_DND_AI.config.config import Config
from Ward_DND_AI.gui.ask.controller_ask import AskController
from Ward_DND_AI.gui.ask.view_ask import AskView
from Ward_DND_AI.gui.browse.controller_browse import BrowseController
from Ward_DND_AI.gui.browse.view_browse import BrowseView
from Ward_DND_AI.gui.campaign_settings.controller_campaign_settings import (
    CampaignSettingsController,
)
from Ward_DND_AI.gui.campaign_settings.view_campaign_settings import (
    CampaignSettingsView,
)
from Ward_DND_AI.gui.help.controller_help import HelpController
from Ward_DND_AI.gui.help.view_help import HelpView
from Ward_DND_AI.gui.random_generator.controller_random_generator import (
    RandomGeneratorController,
)
from Ward_DND_AI.gui.random_generator.view_random_generator import RandomGeneratorView
from Ward_DND_AI.gui.summarize.controller_summarize import SummarizeController
from Ward_DND_AI.gui.summarize.view_summarize import SummarizeView
from Ward_DND_AI.gui.timeline.controller_timeline import TimelineController
from Ward_DND_AI.gui.timeline.view_timeline import TimelineView
from Ward_DND_AI.gui.token.controller_token import TokenController
from Ward_DND_AI.gui.token.view_token import TokenView


class LoreMainApp(ctk.CTk):
    def __init__(self, ai_engine=None, storage_backend=None):
        self.preview_window = None

        self.ai = ai_engine or None
        self.storage = storage_backend or None
        super().__init__()

        self.status_var = tk.StringVar()
        self.title("Obsidian Lore Assistant")
        self.geometry("1024x768")

        self.tabview = ctk.CTkTabview(self, command=self._on_tab_change)
        self.tabview.pack(fill="both", expand=True, padx=10, pady=10)

        # Setup tabs (must come after widgets)
        self._setup_ask_tab()
        self._setup_browse_tab()
        self._setup_summarize_tab()
        self._setup_random_generator_tab()
        self._setup_timeline_tab()
        self._setup_campaign_settings_tab()
        self._setup_help_tab()
        self._setup_token_tab()

        self._setup_menubar()
        self._setup_shortcuts()

        self.status_label = ctk.CTkLabel(
            self, textvariable=self.status_var, font=("Segoe UI", 12, "bold")
        )
        self.status_label.pack(side="bottom", fill="x", pady=(0, 5))

    def _add_tab(self, view_cls, controller_cls, label):
        self.tabview.add(label)
        parent = self.tabview.tab(label)

        try:
            view = view_cls(parent, Config)
        except TypeError:
            view = view_cls(parent)

        setattr(self, f"{label.lower().replace(' ', '_')}_view", view)

        controller = controller_cls(
            view, self.ai, self.storage, Config, self.status_var
        )
        setattr(self, f"{label.lower().replace(' ', '_')}_controller", controller)

        view.frame.grid(row=0, column=0, sticky="nsew")

    def _setup_ask_tab(self):
        self._add_tab(AskView, AskController, "Ask AI")

    def _setup_browse_tab(self):
        self._add_tab(BrowseView, BrowseController, "Browse Vault")

    def _setup_summarize_tab(self):
        self._add_tab(SummarizeView, SummarizeController, "Summarize")

    def _setup_random_generator_tab(self):
        self._add_tab(
            RandomGeneratorView, RandomGeneratorController, "Random Generator"
        )

    def _setup_timeline_tab(self):
        self._add_tab(TimelineView, TimelineController, "Timeline")

    def _setup_campaign_settings_tab(self):
        self._add_tab(
            CampaignSettingsView, CampaignSettingsController, "Campaign Settings"
        )

    def _setup_help_tab(self):
        self._add_tab(HelpView, HelpController, "Help / About")

    def _setup_token_tab(self):
        self._add_tab(TokenView, TokenController, "Tokens")

    def _on_tab_change(self):
        current_tab = self.tabview.get()

        if current_tab == "Browse Vault":
            self.browse_vault_controller.load_folders()

    def _on_tab_change_wrapper(self, event):
        current_tab = self.tabview.get()
        self._on_tab_change(current_tab)

    def _setup_menubar(self):
        menubar = tk.Menu(self)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="New Note", accelerator="Ctrl+N")
        filemenu.add_command(label="Import Note", accelerator="Ctrl+I")
        filemenu.add_command(label="Export Note", accelerator="Ctrl+S")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=filemenu)
        self.config(menu=menubar)

    def _setup_shortcuts(self):
        self.bind_all("<Control-s>", lambda e: self.ask_ai_controller.save_prompt())
        self.bind_all(
            "<Control-Return>", lambda e: self.ask_ai_controller.submit_prompt()
        )

    def open_preview_window(self, content: str):
        if self.preview_window is None or not self.preview_window.winfo_exists():
            self.preview_window = tk.Toplevel(self)
            self.preview_window.title("AI Output Preview")
            self.preview_window.geometry("600x400")

            self.preview_textbox = ctk.CTkTextbox(
                self.preview_window, wrap="word", font=("Consolas", 12)
            )
            self.preview_textbox.pack(fill="both", expand=True, padx=10, pady=10)

        self.preview_textbox.configure(state="normal")
        self.preview_textbox.delete("1.0", "end")
        self.preview_textbox.insert("1.0", content)
        self.preview_textbox.configure(state="disabled")

        self.preview_window.lift()
        self.preview_window.focus()

    @property
    def output_box(self):
        return getattr(self.ask_ai_view, "output_textbox", None)
