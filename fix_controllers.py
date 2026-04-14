"""
Run once to apply AppContext refactor to all controllers.
This script patches every controller's __init__ to accept ctx instead of
individual ai/storage/config parameters.
"""

from pathlib import Path

ROOT = Path(__file__).parent / "Ward_DND_AI"

patches = {
    "gui/browse/controller_browse.py": [
        (
            "def __init__(self, view, ai, storage, config, status_var=None):",
            "def __init__(self, view, ctx, status_var=None):",
        ),
        ("        self.ai = ai", "        self.ctx = ctx\n        self.ai = ctx.ai"),
        ("        self.storage = storage", "        self.storage = ctx.storage"),
        ("        self.config = config", "        self.config = ctx.config"),
    ],
    "gui/chat/controller_chat.py": [
        (
            "def __init__(self, view, ai, storage, config, status_var=None):",
            "def __init__(self, view, ctx, status_var=None):",
        ),
        ("        self.ai = ai", "        self.ctx = ctx\n        self.ai = ctx.ai"),
        ("        self.storage = storage", "        self.storage = ctx.storage"),
        ("        self.config = config", "        self.config = ctx.config"),
    ],
    "gui/create/controller_create.py": [
        (
            "def __init__(self, view, ai_engine, storage, config, status_var=None):",
            "def __init__(self, view, ctx, status_var=None):",
        ),
        ("        self.ai_engine = ai_engine", "        self.ctx = ctx\n        self.ai_engine = ctx.ai"),
        ("        self.storage = storage", "        self.storage = ctx.storage"),
        ("        self.config = config", "        self.config = ctx.config"),
        ("self.view.random_view, ai_engine, storage, config", "self.view.random_view, ctx"),
    ],
    "gui/create/random_generator/controller_random_generator.py": [
        (
            "def __init__(self, view, ai_engine, storage_backend, config, status_var=None):",
            "def __init__(self, view, ctx, status_var=None):",
        ),
        ("        self.ai = ai_engine", "        self.ctx = ctx\n        self.ai = ctx.ai"),
        ("        self.storage = storage_backend", "        self.storage = ctx.storage"),
        ("        self.config = config", "        self.config = ctx.config"),
    ],
    "gui/dashboard/controller_dashboard.py": [
        (
            "def __init__(self, view, ai_engine, storage_backend, config, status_var=None):",
            "def __init__(self, view, ctx, status_var=None):",
        ),
        ("        self.ai_engine = ai_engine", "        self.ctx = ctx\n        self.ai_engine = ctx.ai"),
        ("        self.storage = storage_backend", "        self.storage = ctx.storage"),
        ("        self.config = config", "        self.config = ctx.config"),
    ],
    "gui/settings/controller_settings.py": [
        ("def __init__(self, view, config, ai_engine=None, storage_backend=None):", "def __init__(self, view, ctx):"),
        ("        self.config = config", "        self.ctx = ctx\n        self.config = ctx.config"),
        ("        self.ai_engine = ai_engine", "        self.ai_engine = ctx.ai"),
        ("        self.storage_backend = storage_backend", "        self.storage_backend = ctx.storage"),
        ("self.view.ai_view, self.config, self.ai_engine, self.storage_backend", "self.view.ai_view, self.ctx"),
        (
            "self.view.campaign_view, self.config, self.ai_engine, self.storage_backend",
            "self.view.campaign_view, self.ctx",
        ),
    ],
    "gui/settings/ai/controller_ai.py": [
        ("def __init__(self, view, config, ai_engine, storage_backend=None):", "def __init__(self, view, ctx):"),
        ("        self.config = config", "        self.ctx = ctx\n        self.config = ctx.config"),
        ("        self.ai_engine = ai_engine", "        self.ai_engine = ctx.ai"),
        ("        self.storage_backend = storage_backend", "        self.storage_backend = ctx.storage"),
    ],
    "gui/settings/app/controller_app.py": [
        ("def __init__(self, view, config, app):", "def __init__(self, view, ctx, app):"),
        ("        self.config = config", "        self.ctx = ctx\n        self.config = ctx.config"),
    ],
    "gui/settings/campaign/controller_campaign_settings.py": [
        ("def __init__(self, view, config, storage_backend, ai_engine=None):", "def __init__(self, view, ctx):"),
        ("        self.config = config", "        self.ctx = ctx\n        self.config = ctx.config"),
        ("        self.storage = storage_backend", "        self.storage = ctx.storage"),
        ("        self.ai_engine = ai_engine", "        self.ai_engine = ctx.ai"),
    ],
    "gui/settings/help/controller_help.py": [
        (
            "def __init__(self, view, ai, storage, config, status_var=None):",
            "def __init__(self, view, ctx, status_var=None):",
        ),
        ("        self.ai = ai", "        self.ctx = ctx\n        self.ai = ctx.ai"),
        ("        self.storage = storage", "        self.storage = ctx.storage"),
        ("        self.config = config", "        self.config = ctx.config"),
        ("DebugController(self.v.debug_view, config)", "DebugController(self.v.debug_view, self.ctx)"),
    ],
    "gui/settings/help/debug/controller_debug.py": [
        ("def __init__(self, view, config):", "def __init__(self, view, ctx):"),
        ("        self.config = config", "        self.ctx = ctx\n        self.config = ctx.config"),
    ],
    "gui/universe/controller_universe.py": [
        (
            "def __init__(self, view, ai_engine, storage_backend, config, status_var=None):",
            "def __init__(self, view, ctx, status_var=None):",
        ),
        ("        self.ai = ai_engine", "        self.ctx = ctx\n        self.ai = ctx.ai"),
        ("        self.storage = storage_backend", "        self.storage = ctx.storage"),
        ("        self.config = config", "        self.config = ctx.config"),
    ],
    "gui/universe/timeline/controller_timeline.py": [
        (
            "def __init__(self, view, ai_engine, storage_backend, config, status_var=None):",
            "def __init__(self, view, ctx, status_var=None):",
        ),
        ("        self.ai = ai_engine", "        self.ctx = ctx\n        self.ai = ctx.ai"),
        ("        self.storage = storage_backend", "        self.storage = ctx.storage"),
        ("        self.config = config", "        self.config = ctx.config"),
    ],
    "gui/browse/summarize/controller_summarize.py": [
        (
            "def __init__(self, view, ai_engine, storage, config, status_var=None):",
            "def __init__(self, view, ctx, status_var=None):",
        ),
        ("        self.ai = ai_engine", "        self.ctx = ctx\n        self.ai = ctx.ai"),
        (
            "        self.storage = storage  # Obsidian or file store",
            "        self.storage = ctx.storage  # Obsidian or file store",
        ),
        ("        self.storage = storage", "        self.storage = ctx.storage"),
        ("        self.config = config", "        self.config = ctx.config"),
    ],
}

total_patched = 0
for relpath, ops in patches.items():
    path = ROOT / relpath
    if not path.exists():
        print(f"MISSING: {relpath}")
        continue
    src = path.read_bytes().replace(b"\x00", b"").decode("utf-8")
    file_changed = False
    for old, new in ops:
        if old in src:
            src = src.replace(old, new, 1)
            file_changed = True
    path.write_text(src, encoding="utf-8")
    status = "patched" if file_changed else "already OK"
    print(f"{status}: {relpath}")
    if file_changed:
        total_patched += 1

print(f"\nDone. {total_patched} files updated.")
