import uuid
from datetime import datetime
from typing import List, Optional

import bcrypt

from Ward_DND_AI.models.user import User
from Ward_DND_AI.storage.storage_base import StorageBackend
from Ward_DND_AI.utils.audit_logger import audit


class UserManager:
    """
    Handles all business logic and storage operations for User entities synchronously.
    """

    def __init__(self, storage: StorageBackend):
        self.storage = storage

    def create_user(
        self,
        email: str,
        username: str,
        password: str,
        roles: Optional[List[str]] = None,
        groups: Optional[List[str]] = None,
    ) -> User:
        """
        Create and store a new user with hashed password.
        Raises ValueError if email already exists.
        """
        existing = self.storage.get_user_by_email(email)
        if existing:
            raise ValueError("Email already in use.")

        password_hash = self._hash_password(password)
        user_id = self._generate_id()
        user = User(
            id=user_id,
            owner_id=user_id,  # users own themselves
            email=email,
            username=username,
            password_hash=password_hash,
            roles=roles or ["player"],
            groups=groups or [],
            is_active=True,
            last_login=None,
        )
        self.storage.save_user(user)
        audit("update", "user", user.id, user_id=getattr(user, "owner_id", "system"))
        return user

    def get_user(self, user_id: str) -> Optional[User]:
        return self.storage.get_user_by_id(user_id)

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.storage.get_user_by_email(email)

    def update_user(self, user: User) -> None:
        """
        Update an existing user.
        """
        user.schema_version = max(user.schema_version, 1)
        if not user.last_login:
            user.last_login = datetime.utcnow()
        self.storage.save_user(user)
        audit("update", "user", user.id, user_id=getattr(user, "owner_id", "system"))

    def delete_user(self, user_id: str) -> None:
        """
        Soft-delete user by disabling account.
        """
        user = self.get_user(user_id)
        if user:
            user.is_active = False
            self.update_user(user)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Check if a plaintext password matches the stored hash.
        """
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))

    def _hash_password(self, password: str) -> str:
        """
        Hash a plaintext password using bcrypt.
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def _generate_id(self) -> str:
        """
        Generate a new UUID4 string.
        """
        return str(uuid.uuid4())

    def add_user_to_group(self, user_id: str, group_id: str) -> None:
        """
        Add a user to a group if not already a member.
        """
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found.")
        if group_id not in user.groups:
            user.groups.append(group_id)
            self.update_user(user)

    def remove_user_from_group(self, user_id: str, group_id: str) -> None:
        """
        Remove a user from a group if a member.
        """
        user = self.get_user(user_id)
        if not user:
            raise ValueError("User not found.")
        if group_id in user.groups:
            user.groups.remove(group_id)
            self.update_user(user)

    def check_permission(self, user_id: str, permission: str) -> bool:
        """
        Placeholder for permission check logic.
        """
        user = self.get_user(user_id)
        if not user or not user.is_active:
            return False
        if "admin" in user.roles:
            return True
        # Extend this with actual permission checks later
        return False
