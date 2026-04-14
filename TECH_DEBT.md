# Tech Debt Log — Ward DND AI

Items logged here are known issues that were not fixed immediately.
Each entry has a severity, description, and the conditions under which it should be resolved.

---

## Active Items

### [HIGH] HybridStorage is single-vault only
**File:** `storage/hybrid_storage.py`
**Issue:** `search_notes()` and all path helpers use a single `self.vault_path`. In a true multiuser
system, each user/group may have separate vaults. The `vault_id` parameter is accepted but not used
for isolation.
**Fix when:** Implementing multi-vault / multiplayer storage. Replace HybridStorage with a database
backend (SQLite first, Postgres later) that scopes all queries by `vault_id` and `owner_id`.

### [HIGH] No database backend — file-based storage does not scale for multiuser
**File:** `storage/hybrid_storage.py`
**Issue:** JSON files on disk work for a single user. Concurrent writes, user isolation, and
cross-vault search are not possible without a real database.
**Fix when:** Beginning multiplayer / cloud sync work. Implement a `SQLiteStorageBackend` that
satisfies `StorageBackend` and swap it in via `AppContext`.

### [MEDIUM] controller_browse.py still references `self.storage.vault_path` directly
**File:** `gui/browse/controller_browse.py`
**Issue:** A few path constructions (external editor open, version file path for restore) use
`self.storage.vault_path` directly. This couples the controller to HybridStorage's internal
attribute — other backends may not have `vault_path`.
**Fix when:** Adding a second storage backend. Add an `absolute_path(rel: str) -> str` method to
`StorageBackend` interface.

### [MEDIUM] Version restore in controller_browse reads file directly
**File:** `gui/browse/controller_browse.py` — `open_history_dialog()`
**Issue:** After listing versions via `storage.list_note_versions()`, the restore flow opens the
`.bak` file directly with `open()` rather than calling `storage.restore_note_version()`.
**Fix when:** Any storage refactor. Wire up `storage.restore_note_version(note, version_fname)`.

### [MEDIUM] `storage_router.py` is unused
**File:** `storage/storage_router.py`
**Issue:** The dynamic backend loader exists but `AppContext` hardcodes `HybridStorage`. The router
is the right long-term pattern for swapping backends via config.
**Fix when:** Adding a second backend. Wire `AppContext` to use `storage_router.py` to instantiate
the backend from `settings.json`.

### [LOW] `find_legacy_storage.py` diagnostic script in project root
**File:** `Ward_DND_AI/find_legacy_storage.py`
**Issue:** A one-off diagnostic script left in the source tree.
**Fix when:** Next cleanup pass. Either move to `scripts/` or delete.

### [LOW] `rename_vault_storage.py` migration script in project root
**File:** `Ward_DND_AI/rename_vault_storage.py`
**Issue:** A one-off migration script left in the source tree.
**Fix when:** Next cleanup pass. Move to `scripts/` or delete after confirming migration is complete.

### [LOW] `tree.py` utility script in project root
**File:** `Ward_DND_AI/tree.py`
**Issue:** A directory tree printer left in the source tree, not part of the app.
**Fix when:** Next cleanup pass. Move to `scripts/` or delete.

### [LOW] No mypy type checking configured
**Issue:** Pydantic models are fully typed but the rest of the codebase has no type annotations or
mypy enforcement. Type errors in controllers and managers won't be caught before runtime.
**Fix when:** Section 5 of the foundation checklist.

---

## Resolved Items

| Date | Item | Resolution |
|------|------|------------|
| 2026-04-14 | `file_storage.py` dead code | Deleted |
| 2026-04-14 | API key hardcoded in `settings.json` | Moved to `.env`, key rotated |
| 2026-04-14 | `__pycache__` tracked by git | Added to `.gitignore`, removed from index |
| 2026-04-14 | Black formatter duplicating ruff | Removed black, ruff-format used exclusively |
| 2026-04-14 | All models re-declaring base fields | All models now inherit from `CoreModel` |
| 2026-04-14 | Controllers receiving raw args instead of ctx | All 15 controllers refactored to accept `AppContext` |
| 2026-04-14 | `hybrid_storage.py` using `os.path` throughout | Refactored to `pathlib.Path` |
