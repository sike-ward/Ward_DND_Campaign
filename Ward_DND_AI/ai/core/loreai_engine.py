# Ward_DND_AI/ai/loreai_engine.py

import os
from pathlib import Path
from typing import List, Tuple

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

from Ward_DND_AI.ai.core.ai_base import AIInterface
from Ward_DND_AI.ai.registry import register_plugin
from Ward_DND_AI.config.config import Config


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    """
    Utility to count tokens for a given text and model.
    """
    try:
        import tiktoken

        enc = tiktoken.encoding_for_model(model)
    except (ImportError, AttributeError):
        from tiktoken import get_encoding

        enc = get_encoding("cl100k_base")
    return len(enc.encode(text))


@register_plugin("loreai")
class LoreaiAI(AIInterface):
    """
    LoreAI backend: provides full-text search context capabilities using llama_index.
    Other AI tasks are handled via separate engines orchestrated by ModelRouter.
    """

    def __init__(self, config=None):
        vault_path = None
        api_key = None
        model = "gpt-3.5-turbo"
        if config:
            vault_path = getattr(config, "VAULT_PATH", None)
            api_key = getattr(config, "OPENAI_API_KEY", None)
            model = getattr(config, "COMPLETION_MODEL", model)
        self.vault_path = vault_path
        self.api_key = api_key
        self.model = model
        # rest of your init code

        # Set up OpenAI credentials for embeddings
        os.environ["OPENAI_API_KEY"] = api_key or Config.OPENAI_API_KEY
        self.vault_path = Path(vault_path or Config.VAULT_PATH).resolve()
        self.model = model
        self._initialize_index()

    def _initialize_index(self) -> None:
        """
        Build an in-memory document index for context retrieval.
        """
        Settings.embed_model = OpenAIEmbedding(api_key=os.getenv("OPENAI_API_KEY"))
        docs = SimpleDirectoryReader(str(self.vault_path), recursive=True).load_data()
        for doc in docs:
            if hasattr(doc, "get_doc_id"):
                doc.id_ = doc.get_doc_id()
        index = VectorStoreIndex.from_documents(docs)
        self._retriever = index.as_retriever()
        self._engine = RetrieverQueryEngine(retriever=self._retriever)

    def update_api_key(self, new_key: str):
        if new_key != self.api_key:
            import os

            self.api_key = new_key
            os.environ["OPENAI_API_KEY"] = new_key

            # Clear cached index and engine to force rebuild
            self._retriever = None
            self._engine = None

            # Reinitialize index with the new API key
            self._initialize_index()

    def update_max_tokens(self, max_tokens: int):
        self.max_tokens = max_tokens
        # Reconfigure client if needed

    def update_models(self, embedding_model: str, completion_model: str):
        self.embedding_model = embedding_model
        self.model = completion_model
        # Reinitialize client or parameters if needed

    def ask(self, prompt: str) -> Tuple[str, int, int]:
        """
        Not implemented in LoreaiAI. Use a dedicated LLM engine for 'ask' tasks.
        """
        raise NotImplementedError(
            "Use a dedicated LLM engine for 'ask' tasks via ModelRouter."
        )

    def summarize(self, text: str) -> Tuple[str, int, int]:
        """
        Not implemented in LoreaiAI. Use a dedicated summarization engine.
        """
        raise NotImplementedError(
            "Use a dedicated summarization engine via ModelRouter."
        )

    def suggest_tags(self, text: str) -> Tuple[str, int, int]:
        """
        Not implemented in LoreaiAI. Use a dedicated tag-suggestion engine.
        """
        raise NotImplementedError("Use a dedicated tagging engine via ModelRouter.")

    def propose_links(self, text: str, note_names: List[str]) -> Tuple[str, int, int]:
        """
        Not implemented in LoreaiAI. Use a dedicated link-proposal engine.
        """
        raise NotImplementedError(
            "Use a dedicated link-proposal engine via ModelRouter."
        )

    def search_context(self, query: str, top_k: int = 10) -> List[str]:
        """
        Retrieve up to `top_k` relevant note IDs for the given query.
        """
        docs = self._retriever.retrieve(query)
        return [getattr(doc, "id_", None) for doc in docs][:top_k]
