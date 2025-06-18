# Ward_DND_AI/ai/core/model_router.py

from typing import List, Optional, Tuple

# Import specific AI implementations
from Ward_DND_AI.ai.core.ai_base import AIInterface
from Ward_DND_AI.ai.registry import get_plugin
from Ward_DND_AI.config.config import Config
from Ward_DND_AI.storage.storage_router import get_storage_backend


class ModelRouter(AIInterface):
    """
    Central orchestrator: routes AI tasks to specific backends
    based on configuration and injects vault context into ask().
    """

    TASKS = ["ask", "summarize", "suggest_tags", "propose_links", "search_context"]

    def __init__(self, config: Config):
        self._config = config
        self._backends = {task: self._init_backend(task) for task in self.TASKS}
        print(">>> DEBUG router config:", self._config._data)

    def _init_backend(self, task: str) -> AIInterface:
        # 1. Try per-task override
        key = f"AI_{task.upper()}_BACKEND"
        if hasattr(self._config, key):
            name = getattr(self._config, key)
        # 2. Try AI_BACKENDS dict
        elif isinstance(
            self._config.get("AI_BACKENDS"), dict
        ) and task in self._config.get("AI_BACKENDS"):
            name = self._config.get("AI_BACKENDS")[task]
        # 3. Fallback to global
        else:
            name = getattr(self._config, "AI_BACKEND", None)

        if not name:
            raise ValueError(f"No backend configured for AI task '{task}'")

        plugin_cls = get_plugin(name)
        return plugin_cls(config=self._config)

    def ask(self, prompt: str) -> Tuple[str, int, int]:
        # fetch context
        ids = self.search_context(prompt)
        storage = get_storage_backend(self._config)
        texts = []
        for id_ in ids:
            try:
                texts.append(storage.read_note(id_))
            except Exception:
                pass
        # build prompt
        full = (
            ("Relevant notes:\n\n" + "\n\n".join(texts) + "\n\nUser query:\n" + prompt)
            if texts
            else prompt
        )
        # delegate
        return self._backends["ask"].ask(full)

    def summarize(self, text: str) -> Tuple[str, int, int]:
        return self._backends["summarize"].summarize(text)

    def suggest_tags(self, text: str) -> Tuple[str, int, int]:
        return self._backends["suggest_tags"].suggest_tags(text)

    def propose_links(self, text: str, note_names: List[str]) -> Tuple[str, int, int]:
        return self._backends["propose_links"].propose_links(text, note_names)

    def search_context(self, query: str, top_k: int = 10) -> List[str]:
        return self._backends["search_context"].search_context(query, top_k)

    def get_backend(self, task: str) -> Optional[AIInterface]:
        """Retrieve the backend for a specific AI task."""
        return self._backends.get(task)

    def update_api_key(self, new_key: str):
        self._config.OPENAI_API_KEY = new_key
        for backend in self._backends.values():
            if hasattr(backend, "update_api_key"):
                backend.update_api_key(new_key)

    def update_models(self, embedding_model: str, completion_model: str):
        self._config.EMBEDDING_MODEL = embedding_model
        self._config.COMPLETION_MODEL = completion_model
        for backend in self._backends.values():
            if hasattr(backend, "update_models"):
                backend.update_models(embedding_model, completion_model)

    def update_max_tokens(self, max_tokens: int):
        self._config.MAX_TOKENS = max_tokens
        for backend in self._backends.values():
            if hasattr(backend, "update_max_tokens"):
                backend.update_max_tokens(max_tokens)


def get_model_backend(config: Config) -> AIInterface:
    return ModelRouter(config)
