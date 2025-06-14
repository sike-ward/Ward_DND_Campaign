import os
import time
from pathlib import Path
from typing import Optional, Tuple

import tiktoken

from Ward_DND_AI.ai.model_router import ModelRouter
from Ward_DND_AI.config.config import Config


def count_tokens(text: str, model: str = "gpt-3.5-turbo") -> int:
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))


class LoreAI:
    def __init__(
        self,
        vault_path: Optional[str] = None,
        api_key: Optional[str] = None,
        model: str = "gpt-3.5",
    ):
        # Set OpenAI key before llama_index uses it
        os.environ["OPENAI_API_KEY"] = api_key or Config.OPENAI_API_KEY

        self.vault_path = Path(vault_path or Config.VAULT_PATH).resolve()
        self.api_key = api_key or Config.OPENAI_API_KEY
        self.model = model

        self.router = ModelRouter(model=self.model, api_key=self.api_key)
        self.cache = {}
        self.reload_data()

    def reload_data(self):
        from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
        from llama_index.core.query_engine import RetrieverQueryEngine
        from llama_index.core.settings import Settings
        from llama_index.embeddings.openai import OpenAIEmbedding

        # Set embedding model with key explicitly
        Settings.embed_model = OpenAIEmbedding(api_key=self.api_key)

        documents = SimpleDirectoryReader(
            str(self.vault_path), recursive=True
        ).load_data()
        for doc in documents:
            if hasattr(doc, "get_doc_id"):
                doc.id_ = doc.get_doc_id()

        self.index = VectorStoreIndex.from_documents(documents)
        retriever = self.index.as_retriever()
        self.engine = RetrieverQueryEngine(retriever=retriever)

    def query(self, question: str) -> str:
        return str(self.engine.query(question))

    def _llm_prompt(self, prompt: str, system: Optional[str] = None) -> str:
        cache_key = (prompt.strip(), system or "")
        if cache_key in self.cache:
            return self.cache[cache_key]

        for attempt in range(3):
            try:
                response = self.router.query(prompt, system)
                self.cache[cache_key] = response
                return response
            except Exception as e:
                if attempt < 2:
                    time.sleep(2**attempt)
                else:
                    raise RuntimeError(f"LLM query failed after retries: {e}")

    def summarize(self, text: str, model: Optional[str] = None) -> Tuple[str, int, int]:
        prompt = f"Summarize this note in a single concise paragraph (no more than 4 sentences):\n\n{text}"
        prompt_tokens = count_tokens(prompt, model or self.model)
        response = self._llm_prompt(prompt)
        response_tokens = count_tokens(str(response), model or self.model)
        return response, prompt_tokens, response_tokens

    def suggest_tags(
        self, text: str, model: Optional[str] = None
    ) -> Tuple[str, int, int]:
        prompt = (
            "Suggest 3-7 useful tags (keywords or phrases) for this note, "
            "comma separated. Just give the tags:\n\n" + text
        )
        prompt_tokens = count_tokens(prompt, model or self.model)
        response = self._llm_prompt(prompt)
        response_tokens = count_tokens(str(response), model or self.model)
        return response, prompt_tokens, response_tokens

    def propose_links(
        self, text: str, note_names: list[str], model: Optional[str] = None
    ) -> Tuple[str, int, int]:
        prompt = (
            f"Based on the following note, suggest any likely Obsidian-style internal links "
            f"(choose only from this list: {', '.join(note_names)}).\n"
            "Return just a list of matching note names:\n\n"
            f"{text}"
        )
        prompt_tokens = count_tokens(prompt, model or self.model)
        response = self._llm_prompt(prompt)
        response_tokens = count_tokens(str(response), model or self.model)
        return response, prompt_tokens, response_tokens
