# Ward DND Campaign App — Foundation & Features Checklist

---

## 1. Core Data Models & Types ✅

- [x] List all core data types (notes, folders, vaults, users, campaigns, attachments, characters, maps, etc.)
- [x] Design typed, validated models (`pydantic` or `dataclass`) for every core entity
- [x] Every model has a `schema_version` field
- [x] Each model has `created_at`, `last_modified`, and `owner_user_id/group_id` fields
- [x] Docstrings for every class and field (required by lint/type check/review)
- [x] Any new model type gets added to the models folder immediately

---

## 2. AppContext / Service Registry ✅

- [x] Single `AppContext` class holds all managers/services (config, storage, ai, session, user manager, etc.)
- [x] All controllers/views receive `AppContext` (no raw globals/direct imports)
- [x] Every field in `AppContext` is documented

---

## 3. Config, Secrets, and Environment

- [x] `.env` and/or `config.py` loads all secrets/paths/env (never hardcoded)
- [x] `AppContext` references config, not raw env vars
- [ ] Dev/prod/test config separation, documented
- [ ] All file/folder paths use `pathlib.Path` or are platform-agnostic

---

## 4. Storage, Dependency, and Code Hygiene

- [ ] Use only one storage backend everywhere (`storage`)
- [ ] Move/refactor any business/data logic out of views into controllers or services
- [ ] Delete all legacy backends, split variables, and dead code (no `file_storage.py`, `obsidian_storage.py`, or “core_storage” remains)
- [ ] Any hacks/tech debt found is logged in `TECH_DEBT.md` immediately

---

## 5. Logging, Backup, and Testing

- [ ] Basic audit/event logging (every create/update/delete logs a line in `audit.log`)
- [ ] Set up automatic backups (user-accessible, test restore)
- [ ] Smoke/integration test for every model’s CRUD (manual script or pytest)
- [ ] Lint and type-check the codebase (`ruff`, `mypy` all pass on every commit)
- [ ] Add mypy config to repo

---

## 6. UI/UX and Security

- [ ] No hardcoded UI text or unlocalizable strings (UI uses variables/config for all user-facing text)
- [ ] Add simple user/session login or “current user” context (even hardcoded for now)
- [ ] Enforce permissions (read/write/owner) for all per-vault actions (basic ACL/permissions structure in place, ready to expand)

---

## 7. Documentation & Compliance

- [ ] Create or update `README.md` and stub out `/docs/`
- [ ] Docs folder contains migration/upgrade path, backup/restore, permissions model, and config reference
- [ ] Config and usage docs up to date (only new backend/workflow)
- [ ] Docstrings/comments required by linting for all functions/classes

---

## 8. Data Portability & Disaster Recovery

- [ ] Export ALL user data from the app (notes, models, logs, settings)
- [ ] Test simulated disaster recovery (restore from backup, migrate old to new format)

---

## --- ✅ WHEN THESE ARE ALL CHECKED, YOU MAY ADD/EXPAND USER-FACING FEATURES! ---

---

## 🎉 Now You Can Build/Expand App Features:

- [ ] Refactor and expand AI/Ask tab handling
- [ ] Add campaign, timeline, world/lore, or “map” features
- [ ] Begin integrating or refactoring summarize/bulk/graph features
- [ ] Implement real user auth: user signup/login/logout, password hashing, session tokens
- [ ] Hook up group logic and per-vault permissions
- [ ] Surface model metadata (maps, characters, etc.) in GUI or AI prompts
- [ ] Add new “Browse” submodules (tree, tags, dialogs, versioning, etc.)
- [ ] Integrate multiplayer, cloud sync, or any advanced feature
- [ ] Add usage analytics, rate limiting, performance profiling, etc.

---

> **Pro Tip:**  
> As you add each new feature, always:
> - Use only the storage backend (never direct file I/O).
> - Enforce current user/context everywhere.
> - Write at least a smoke test for new models/features.
> - Document major additions/changes in `/docs/` or your README.

---

**If you want templates, code samples, or step-by-step help on any box, just ask!**
## Advanced/Polish/Release Items

- [ ] Set up CI/CD (tests, build, release)
- [ ] Accessibility and localization ready (screen reader, font scaling, i18n)
- [x] Global error/crash handler with user-friendly logs
- [ ] Data export/delete/backup fully documented for users
- [ ] Privacy/compliance docs (if public/online)
- [ ] Plugin/extension API planned and stubbed
- [ ] Performance tested for large vaults/notes
- [ ] Backup/restore UI for users
- [ ] In-app help/FAQ, feedback links
- [ ] Versioning and upgrade flow with changelog/auto-migrate
- [ ] Regular tech debt review and codebase health check







