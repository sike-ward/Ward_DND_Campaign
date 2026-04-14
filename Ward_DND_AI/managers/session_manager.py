from datetime import datetime, timedelta
from typing import Optional

from Ward_DND_AI.models.session import Session
from Ward_DND_AI.storage.storage_base import StorageBackend


class SessionManager:
    """
    Handles business logic and storage for user login sessions synchronously.
    """

    def __init__(self, storage: StorageBackend, session_duration_minutes: int = 60):
        self.storage = storage
        self.session_duration = timedelta(minutes=session_duration_minutes)

    def create_session(
        self,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> Session:
        """
        Create a new session for a user with expiration.
        """
        now = datetime.utcnow()
        session = Session(
            id=self._generate_id(),
            user_id=user_id,
            created_at=now,
            expires_at=now + self.session_duration,
            refresh_token=None,
            ip_address=ip_address,
            user_agent=user_agent,
            context={},
            is_active=True,
            schema_version=1,
        )
        self.storage.save_session(session)
        return session

    def get_session(self, session_id: str) -> Optional[Session]:
        return self.storage.get_session_by_id(session_id)

    def refresh_session(self, session_id: str) -> None:
        """
        Extend session expiry.
        """
        session = self.get_session(session_id)
        if session and session.is_active:
            session.expires_at = datetime.utcnow() + self.session_duration
            self.storage.save_session(session)

    def revoke_session(self, session_id: str) -> None:
        """
        Mark a session as inactive (logout).
        """
        session = self.get_session(session_id)
        if session:
            session.is_active = False
            self.storage.save_session(session)

    def is_session_valid(self, session_id: str) -> bool:
        session = self.get_session(session_id)
        if not session or not session.is_active:
            return False
        return datetime.utcnow() < session.expires_at

    def _generate_id(self) -> str:
        import uuid

        return str(uuid.uuid4())
