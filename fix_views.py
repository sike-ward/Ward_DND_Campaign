"""
Run once to fix view signatures — replaces (ai_engine, config) with ctx
where needed, and fixes gui.py to pass ctx.config to views that only need config.
"""

from pathlib import Path

ROOT = Path(__file__).parent / "Ward_DND_AI"

# Views that take (parent, ai_engine, config) -> (parent, ctx)
# or (parent, config, ai_engine) -> (parent, ctx)
view_patches = {
    "gui/settings/view_settings.py": [
        ("def __init__(self, parent, ai_engine, config):", "def __init__(self, parent, ctx):"),
        (
            "        self.ai_engine = ai_engine\n        self.config = config",
            "        self.ctx = ctx\n        self.ai_engine = ctx.ai\n        self.config = ctx.config",
        ),
        ("        self.ai_engine = ai_engine", "        self.ai_engine = ctx.ai"),
        ("        self.config = config", "        self.ctx = ctx\n        self.config = ctx.config"),
        # Fix AISettingsView instantiation call inside view_settings
        ("AISettingsView(self, self.config, self.ai_engine)", "AISettingsView(self, self.ctx)"),
    ],
    "gui/settings/ai/view_ai.py": [
        ("def __init__(self, parent, config, ai_engine):", "def __init__(self, parent, ctx):"),
        ("        self.config = config", "        self.ctx = ctx\n        self.config = ctx.config"),
        ("        self.ai_engine = ai_engine", "        self.ai_engine = ctx.ai"),
    ],
}

# gui.py: fix the one wrong view call (SettingsView gets ctx, others keep config)
gui_patches = [
    # SettingsView was changed to pass ctx - that's correct now
    # Other views still use self._config which is fine
]

print("=== Patching views ===")
for relpath, ops in view_patches.items():
    path = ROOT / relpath
    if not path.exists():
        print(f"MISSING: {relpath}")
        continue
    src = path.read_bytes().replace(b"\x00", b"").decode("utf-8")
    changed = False
    for old, new in ops:
        if old in src:
            src = src.replace(old, new, 1)
            changed = True
            print(f"  patched: {old.strip()[:60]!r}")
    path.write_text(src, encoding="utf-8")
    print(f"  {'saved' if changed else 'already OK'}: {relpath}")

# Also fix gui.py - DashboardView, ChatView etc. still get self._config which is fine
# But SettingsView now needs ctx - let's verify gui.py has it right
gui_path = ROOT / "gui/gui.py"
gui_src = gui_path.read_bytes().replace(b"\x00", b"").decode("utf-8")

# SettingsView should get self.ctx (already changed), but check it
if "SettingsView(self.tabview, self.ctx)" in gui_src:
    print("\n  gui.py SettingsView call: OK (passes ctx)")
elif "SettingsView(self.tabview, self.ai, self._config)" in gui_src:
    gui_src = gui_src.replace(
        "SettingsView(self.tabview, self.ai, self._config)", "SettingsView(self.tabview, self.ctx)"
    )
    gui_path.write_text(gui_src, encoding="utf-8")
    print("\n  gui.py SettingsView call: fixed")
else:
    print("\n  gui.py SettingsView: check manually")

# Fix sub-controller calls inside controller_settings.py
cs_path = ROOT / "gui/settings/controller_settings.py"
cs_src = cs_path.read_bytes().replace(b"\x00", b"").decode("utf-8")
cs_patches = [
    # \r line endings - match both variants
    (
        "HelpController(\r            self.view.help_view, self.config, self.ai_engine, self.storage_backend\r        )",
        "HelpController(self.view.help_view, self.ctx)",
    ),
    (
        "HelpController(\n            self.view.help_view, self.config, self.ai_engine, self.storage_backend\n        )",
        "HelpController(self.view.help_view, self.ctx)",
    ),
    (
        "AppSettingsController(\r            self.view.app_settings_view,\r            self.config,\r            None,  # pass QApplication.instance() if you need the app\r        )",
        "AppSettingsController(self.view.app_settings_view, self.ctx, None)",
    ),
    (
        "AppSettingsController(\n            self.view.app_settings_view,\n            self.config,\n            None,  # pass QApplication.instance() if you need the app\n        )",
        "AppSettingsController(self.view.app_settings_view, self.ctx, None)",
    ),
]
cs_changed = False
for old, new in cs_patches:
    if old in cs_src:
        cs_src = cs_src.replace(old, new, 1)
        cs_changed = True
        print(f"  patched controller_settings: {old.strip()[:50]!r}")
if cs_changed:
    cs_path.write_text(cs_src, encoding="utf-8")
    print("  saved: controller_settings.py")
else:
    print("  already OK: controller_settings.py")

print("\nDone.")
