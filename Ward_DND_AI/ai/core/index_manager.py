# Ward_DND_AI/ai/core/index_manager.py

import os
from pathlib import Path

from llama_index.core import (
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from llama_index.core.settings import Settings
from llama_index.embeddings.openai import OpenAIEmbedding


class IndexManager:
    """
    Centralizes all index building, updating, and searching.
    Any AI task can use this class for fast and efficient context retrieval.
    """

    def __init__(self, vault_path, api_key, embedding_model="text-embedding-ada-002"):
        self.vault_path = Path(vault_path).resolve()
        self.api_key = api_key
        self.embedding_model = embedding_model
        self.index_dir = str(self.vault_path / "loreai_index")
        self.index = None
        self._retriever = None
        self._engine = None
        self._init_index()

    def _init_index(self):
        os.environ["OPENAI_API_KEY"] = self.api_key
        Settings.embed_model = OpenAIEmbedding(
            api_key=self.api_key, model=self.embedding_model
        )
        if os.path.exists(self.index_dir):
            # Load persistent index
            storage_context = StorageContext.from_defaults(persist_dir=self.index_dir)
            self.index = load_index_from_storage(storage_context)
        else:
            # Create and persist index
            docs = SimpleDirectoryReader(
                str(self.vault_path), recursive=True
            ).load_data()
            for doc in docs:
                if hasattr(doc, "get_doc_id"):
                    doc.id_ = doc.get_doc_id()
            self.index = VectorStoreIndex.from_documents(docs)
            self.index.storage_context.persist(persist_dir=self.index_dir)
        self._retriever = self.index.as_retriever()

    def search(self, query, top_k=10):
        """Return up to top_k relevant note IDs for a query."""
        docs = self._retriever.retrieve(query)
        return [getattr(doc, "id_", None) for doc in docs][:top_k]

    def rebuild(self):
        """Force a full rebuild of the index from disk."""
        if os.path.exists(self.index_dir):
            import shutil

            shutil.rmtree(self.index_dir)
        self._init_index()

    def update_for_note(self, note_path):
        """
        Incrementally update the index for a specific note.
        (Not implemented: LlamaIndex only recently added proper incremental update APIs.
        Placeholder for future upgrades.)
        """
        pass

    def delete_note(self, note_id):
        """
        Remove a note from the index.
        (Not implemented: Placeholder for future if/when llama_index supports live removal.)
        """
        pass

    def get_index(self):
        """Direct access to the underlying index (if needed for advanced ops)."""
        return self.index
