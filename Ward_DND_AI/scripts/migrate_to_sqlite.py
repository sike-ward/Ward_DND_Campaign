"""
migrate_to_sqlite.py — Migrate existing HybridStorage data to SQLite.

Run this once if you have existing data from a previous version.
New installs do NOT need to run this — the app creates a fresh SQLite DB automatically.

Usage:
    python Ward_DND_AI/scripts/migrate_to_sqlite.py

What it migrates:
  - Users and groups from ~/.ward_dnd_ai/
  - All .dnd_meta/ JSON model records (vaults, notes, characters, maps, etc.)
  - Starred notes list

What it does NOT migrate (stays on filesystem — that's correct):
  - Markdown note files (still read/written as .md files)
  - .versions/ backup files
  - Attachments
"""

import json
import sys
from pathlib import Path

# Ensure project root is on path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from Ward_DND_AI.config.config import Config
from Ward_DND_AI.storage.hybrid_storage import HybridStorage
from Ward_DND_AI.storage.sqlite_backend import SQLiteStorageBackend


def migrate():
    print("Ward DND AI — SQLite Migration")
    print("=" * 50)

    config = Config()
    vault_path = Path(config.VAULT_PATH).resolve()

    if not vault_path.exists():
        print(f"ERROR: Vault path does not exist: {vault_path}")
        sys.exit(1)

    # Source: HybridStorage
    source = HybridStorage(str(vault_path))

    # Destination: SQLite
    db_path = vault_path.parent / "ward_dnd.db"
    if db_path.exists():
        print(f"WARNING: {db_path} already exists.")
        answer = input("Overwrite? This will REPLACE existing SQLite data. [y/N]: ")
        if answer.lower() != "y":
            print("Aborted.")
            sys.exit(0)
        db_path.unlink()

    dest = SQLiteStorageBackend(db_path=str(db_path), vault_path=str(vault_path))
    print(f"  Source: {vault_path} (HybridStorage)")
    print(f"  Destination: {db_path} (SQLite)")
    print()

    counts = {}

    # --- Users ---
    users_file = Path("~/.ward_dnd_ai/users.json").expanduser()
    if users_file.exists():
        raw = json.loads(users_file.read_text(encoding="utf-8"))
        from Ward_DND_AI.models.user import User

        for uid, data in raw.items():
            try:
                user = User.model_validate(data)
                dest.save_user(user)
            except Exception as e:
                print(f"  SKIP user {uid}: {e}")
        counts["users"] = len(raw)
        print(f"  Migrated {len(raw)} users")

    # --- Groups ---
    groups_file = Path("~/.ward_dnd_ai/groups.json").expanduser()
    if groups_file.exists():
        raw = json.loads(groups_file.read_text(encoding="utf-8"))
        from Ward_DND_AI.models.group import Group

        for gid, data in raw.items():
            try:
                group = Group.model_validate(data)
                dest.save_group(group)
            except Exception as e:
                print(f"  SKIP group {gid}: {e}")
        counts["groups"] = len(raw)
        print(f"  Migrated {len(raw)} groups")

    # --- DND Meta records ---
    dnd_meta = vault_path / ".dnd_meta"
    if dnd_meta.exists():
        model_map = {
            "vaults": ("Ward_DND_AI.models.vault", "Vault", dest.save_vault),
            "notes": ("Ward_DND_AI.models.note", "Note", dest.save_note),
            "characters": ("Ward_DND_AI.models.character", "Character", dest.save_character),
            "maps": ("Ward_DND_AI.models.map", "Map", dest.save_map),
            "images": ("Ward_DND_AI.models.image", "Image", dest.save_image),
            "sounds": ("Ward_DND_AI.models.sound", "Sound", dest.save_sound),
            "folders": ("Ward_DND_AI.models.folder", "Folder", dest.save_folder),
            "sessions": ("Ward_DND_AI.models.session", "Session", dest.save_session),
        }

        for subfolder, (module_path, class_name, save_fn) in model_map.items():
            subdir = dnd_meta / subfolder
            if not subdir.exists():
                continue
            import importlib

            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            migrated = 0
            for json_file in subdir.glob("*.json"):
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                    obj = cls.model_validate(data)
                    save_fn(obj)
                    migrated += 1
                except Exception as e:
                    print(f"  SKIP {subfolder}/{json_file.name}: {e}")
            counts[subfolder] = migrated
            print(f"  Migrated {migrated} {subfolder}")

    # --- Starred notes ---
    try:
        starred = source.read_starred()
        if starred:
            dest.write_starred(starred)
            print(f"  Migrated {len(starred)} starred notes")
    except Exception as e:
        print(f"  SKIP starred: {e}")

    print()
    print("Migration complete!")
    print(f"  Database: {db_path}")
    print(f"  Total records: {sum(counts.values())}")
    print()
    print("Your markdown files and attachments stay in the vault — no changes there.")
    print("You can now launch the app normally.")


if __name__ == "__main__":
    migrate()
