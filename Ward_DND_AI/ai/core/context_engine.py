# Ward_DND_AI/ai/core/context_engine.py

from typing import List

from Ward_DND_AI.ai.core.loreai_engine import LoreaiAI
from Ward_DND_AI.config.config import Config
from Ward_DND_AI.storage.storage_router import get_storage_backend


class ContextEngine:
    """
    Provides vault context for any query:
      - Uses LoreaiAI.search_context(...) to get top-K note IDs.
      - Reads each note via the StorageRouter.
      - Returns the raw note texts or a single concatenated block.
    """

    def __init__(self, config: Config):
        self._config = config
        self._retriever = LoreaiAI(
            vault_path=config.VAULT_PATH,
            api_key=config.OPENAI_API_KEY,
            model=config.AI_MODEL,
        )
        self._storage = get_storage_backend(config)

    def get_texts(self, query: str, top_k: int = 10) -> List[str]:
        ids = self._retriever.search_context(query, top_k)
        texts = []
        for note_id in ids:
            try:
                texts.append(self._storage.read_note(note_id))
            except Exception:
                continue
        return texts

    def build_prompt(self, query: str, top_k: int = 10) -> str:
        texts = self.get_texts(query, top_k)
        if not texts:
            return query
        block = "\n\n".join(texts)
        return f"Relevant notes:\n\n{block}\n\nUser query:\n{query}"
