from datetime import datetime
from typing import Dict, List, Optional

from Ward_DND_AI.models.vault import Vault
from Ward_DND_AI.storage.storage_base import StorageBackend


class VaultManager:
    """
    Handles all business logic and storage operations for Vault entities synchronously.
    """

    def __init__(self, storage: StorageBackend):
        self.storage = storage

    def create_vault(
        self,
        name: str,
        owner_id: str,
        description: Optional[str] = None,
        members: Optional[List[str]] = None,
        roles: Optional[List[str]] = None,
        settings: Optional[Dict[str, str]] = None,
        permissions: Optional[Dict[str, str]] = None,
    ) -> Vault:
        """
        Create and store a new vault/campaign.
        """
        vault = Vault(
            id=self._generate_id(),
            name=name,
            owner_id=owner_id,
            description=description,
            members=members or [],
            roles=roles or ["player"],
            settings=settings or {},
            permissions=permissions or {},
            is_active=True,
            created_at=datetime.utcnow(),
            schema_version=1,
            version=1,
        )
        self.storage.save_vault(vault)
        return vault

    def get_vault(self, vault_id: str) -> Optional[Vault]:
        return self.storage.get_vault_by_id(vault_id)

    def update_vault(self, vault: Vault) -> None:
        vault.schema_version = max(vault.schema_version, 1)
        vault.version += 1
        self.storage.save_vault(vault)

    def delete_vault(self, vault_id: str) -> None:
        vault = self.get_vault(vault_id)
        if vault:
            vault.is_active = False
            self.update_vault(vault)

    def add_member(self, vault_id: str, user_id: str) -> None:
        vault = self.get_vault(vault_id)
        if not vault:
            raise ValueError("Vault not found.")
        if user_id not in vault.members:
            vault.members.append(user_id)
            self.update_vault(vault)

    def remove_member(self, vault_id: str, user_id: str) -> None:
        vault = self.get_vault(vault_id)
        if not vault:
            raise ValueError("Vault not found.")
        if user_id in vault.members:
            vault.members.remove(user_id)
            self.update_vault(vault)

    def check_permission(self, vault_id: str, user_id: str, permission: str) -> bool:
        vault = self.get_vault(vault_id)
        if not vault or not vault.is_active:
            return False
        if user_id in vault.members and "admin" in vault.roles:
            return True
        # Extend with your permission rules
        return False

    def _generate_id(self) -> str:
        import uuid

        return str(uuid.uuid4())
