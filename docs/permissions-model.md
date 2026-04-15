# Permissions Model

Ward DND AI uses a simple, extensible ACL (Access Control List) system designed to grow into full multiuser support.

---

## How It Works

Every data record (Note, Vault, Character, etc.) carries two fields:

```python
owner_id: str        # User ID of the creator — always has full access
permissions: dict    # {user_id: role} overrides — e.g. {"u-abc": "read"}
```

The `PermissionChecker` (`auth/permission_checker.py`) evaluates access using these rules, checked in order:

1. **System actor** (`user_id == "system"`) — always granted (for background operations)
2. **Owner** (`user_id == resource.owner_id`) — always granted full access
3. **Explicit permission** — checks `resource.permissions[user_id]` for a role
4. **Default** — deny

---

## Roles

| Role | Can Read | Can Write | Can Delete |
|------|----------|-----------|------------|
| `read` | ✅ | ❌ | ❌ |
| `write` | ✅ | ✅ | ❌ |
| `admin` | ✅ | ✅ | ✅ |

---

## Usage in Managers

```python
from Ward_DND_AI.auth.permission_checker import permissions

# Raise PermissionError if user cannot write
permissions.require_write(note, actor_id=ctx.current_user_id)

# Check without raising
if permissions.can_read(vault, user_id):
    ...
```

---

## Current State (Single-User Mode)

In the current single-user build:
- A default `local@ward-dnd.local` user is created on first launch
- `ctx.current_user_id` is set to this user's ID at startup
- All records created by this user have `owner_id` matching `current_user_id`
- Permissions are enforced on `NoteManager.update_note()`, `delete_note()`, and `VaultManager.delete_vault()`

---

## Multiuser Expansion Path

When adding real multiuser support:

1. Replace the default local user creation in `main.py` with a real login flow
2. Set `ctx.current_user_id` from the authenticated session token
3. Add group membership lookups to `PermissionChecker._has_role()` to support group-level permissions
4. Add vault-level default permissions that child resources inherit
5. Add a database backend that can query by `vault_id` and `owner_id` efficiently
