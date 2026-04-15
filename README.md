# Ward DND AI

An AI-powered assistant for managing your Obsidian D&D vault. Browse notes, ask questions about your lore, generate summaries, suggest tags, and manage characters, maps, timelines, and more — all from a desktop GUI backed by your local Obsidian vault.

---

## Quick Start

### Requirements
- Python 3.11+
- An OpenAI API key
- An Obsidian vault (or any folder of markdown files)

### Install

```bash
git clone https://github.com/sike-ward/Ward_DND_Campaign.git
cd Ward_DND_Campaign
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env and set your OPENAI_API_KEY and VAULT_PATH
```

### Run

```bash
python Ward_DND_AI\main.py
# or double-click Launch_Lore_App.bat
```

---

## Environment Configuration

The app uses `.env` files for secrets and environment-specific settings.

| File | Purpose |
|------|---------|
| `.env` | Shared secrets — **never commit this** |
| `.env.development` | Local dev overrides (optional) |
| `.env.production` | Production overrides (optional) |
| `.env.test` | Test environment overrides (optional) |
| `.env.example` | Template — safe to commit |

Set `APP_ENV=production` in your shell to switch environments.

Key variables:

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | Your OpenAI API key |
| `VAULT_PATH` | Absolute path to your Obsidian vault |
| `APP_ENV` | `development` (default), `production`, or `test` |
| `LOG_LEVEL` | `DEBUG`, `INFO`, `WARNING` (default: `INFO`) |
| `COMPLETION_MODEL` | OpenAI model for chat (default: `gpt-4o`) |
| `EMBEDDING_MODEL` | OpenAI model for embeddings (default: `text-embedding-3-small`) |

All other settings live in `Ward_DND_AI/config/settings.json` and can be changed from the Settings tab inside the app.

---

## Project Structure

```
Ward_DND_Campaign/
├── Ward_DND_AI/
│   ├── ai/           # AI engines (OpenAI, LoreAI RAG)
│   ├── auth/         # PermissionChecker, session management
│   ├── config/       # Config loader, settings.json, templates
│   ├── context/      # AppContext — central service locator
│   ├── gui/          # PyQt6 GUI (controllers + views per tab)
│   ├── managers/     # Business logic layer (one per model type)
│   ├── models/       # Pydantic data models
│   ├── storage/      # StorageBackend interface + HybridStorage
│   ├── tests/        # pytest test suite
│   └── utils/        # Crash handler, audit logger, helpers
├── docs/             # Architecture and operational docs
├── logs/             # app.log, audit.log, crash logs
├── .env.example      # Environment variable template
├── mypy.ini          # Type checking config
├── TECH_DEBT.md      # Known issues and deferred work
└── requirements.txt  # Python dependencies
```

---

## Architecture Overview

The app follows a strict MVC pattern with dependency injection:

- **Models** (`models/`) — Pydantic v2, all inherit from `CoreModel` which provides `id`, `schema_version`, `owner_id`, `created_at`, `last_modified`
- **Storage** (`storage/`) — `StorageBackend` abstract interface; `HybridStorage` stores notes as markdown and structured data as JSON in `.dnd_meta/`
- **Managers** (`managers/`) — Business logic; one manager per model type; all take `StorageBackend` via constructor
- **AppContext** (`context/app_context.py`) — Single service locator passed to every controller; holds config, storage, AI engine, all managers, and permission checker
- **Controllers/Views** (`gui/`) — PyQt6 MVC; controllers receive `ctx: AppContext` and never touch storage or files directly

### Multiuser Design

Every model record carries `owner_id` and a `permissions` dict. `PermissionChecker` (`auth/permission_checker.py`) enforces read/write/admin access. `AppContext.current_user_id` identifies the acting user. When a database backend is added, swap `HybridStorage` for a new `StorageBackend` implementation in `AppContext.__init__` — nothing else needs to change.

---

## Docs

- [Configuration Reference](docs/config-reference.md)
- [Permissions Model](docs/permissions-model.md)
- [Backup & Restore](docs/backup-restore.md)
- [Migration & Upgrade Guide](docs/migration-upgrade.md)

---

## Development

```bash
# Lint + format
ruff check .
ruff format .

# Tests
pytest Ward_DND_AI/tests/

# Type check
mypy Ward_DND_AI/models/ Ward_DND_AI/managers/ Ward_DND_AI/storage/

# Export all user data
python Ward_DND_AI/scripts/export_data.py --output exports/
```

Pre-commit hooks run ruff automatically on every commit.

---

## License

Private project — all rights reserved.
