# Ward_DND_AI/ai/core/model_router.py

from typing import List, Optional, Tuple

from Ward_DND_AI.ai.ai_logging import estimate_cost, log_api_call

# Import specific AI implementations
from Ward_DND_AI.ai.core.ai_base import AIInterface
from Ward_DND_AI.ai.core.context_assembler import ContextAssembler
from Ward_DND_AI.ai.core.index_manager import IndexManager
from Ward_DND_AI.ai.core.openai_engine import count_tokens
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
            # Build context using ContextAssembler

            # Get model and token limit from config or use default
            model_name = getattr(self._backends["ask"], "model", "gpt-3.5-turbo")
            max_context_tokens = getattr(
                self._config, "MAX_CONTEXT_TOKENS", 4096
            )  # can update config later

            # Set up index manager (ideally move this to __init__ for reuse)
            if not hasattr(self, "_index_manager") or self._index_manager is None:
                self._index_manager = IndexManager(
                    vault_path=getattr(self._config, "VAULT_PATH", ""),
                    api_key=getattr(self._config, "OPENAI_API_KEY", ""),
                    embedding_model=getattr(
                        self._config, "EMBEDDING_MODEL", "text-embedding-ada-002"
                    ),
                )
            # Get storage backend
            storage = get_storage_backend(self._config)

            # Assemble context window
            assembler = ContextAssembler(
                index_manager=self._index_manager,
                storage=storage,
                model=model_name,
                max_context_tokens=max_context_tokens,
            )
            ctx_result = assembler.assemble_context(
                prompt, task="ask", top_k=5, min_tokens_for_reply=256
            )
            full_prompt = ctx_result["context_block"]

            # Log context truncation if it happened
            if ctx_result["truncated"]:
                print(
                    f"[WARN] Context truncated in ModelRouter.ask: only {len(ctx_result['included_ids'])} notes fit in prompt window."
                )

            prompt_tokens = count_tokens(full_prompt, model_name)

            log_api_call(
                model_name,
                "ask",
                prompt_tokens,
                0,  # We don't know completion tokens yet
                estimate_cost(model_name, prompt_tokens, 0),
                success=True,
                error_msg=f"context_note_ids={ctx_result['included_ids']}",
                prompt=full_prompt,
            )

            # Delegate to backend (e.g., OpenaiAI)
            result = self._backends["ask"].ask(full_prompt)
            return result

    def summarize(self, text: str) -> Tuple[str, int, int]:
        # For summarize, just pass the note as context

        model_name = getattr(self._backends["summarize"], "model", "gpt-3.5-turbo")
        max_context_tokens = getattr(self._config, "MAX_CONTEXT_TOKENS", 4096)

        if not hasattr(self, "_index_manager") or self._index_manager is None:
            self._index_manager = IndexManager(
                vault_path=getattr(self._config, "VAULT_PATH", ""),
                api_key=getattr(self._config, "OPENAI_API_KEY", ""),
                embedding_model=getattr(
                    self._config, "EMBEDDING_MODEL", "text-embedding-ada-002"
                ),
            )
        storage = get_storage_backend(self._config)

        assembler = ContextAssembler(
            index_manager=self._index_manager,
            storage=storage,
            model=model_name,
            max_context_tokens=max_context_tokens,
        )
        # Here we treat the input as a 'note', no extra context
        ctx_result = assembler.assemble_context(
            query="",  # No search
            task="summarize",
            top_k=0,
            extra_ids=[],
            user_prompt=f"Summarize the following note:\n\n{text}",
            min_tokens_for_reply=256,
        )
        prompt_to_send = ctx_result["context_block"]
        return self._backends["summarize"].summarize(prompt_to_send)

    def suggest_tags(self, text: str) -> Tuple[str, int, int]:
        model_name = getattr(self._backends["suggest_tags"], "model", "gpt-3.5-turbo")
        max_context_tokens = getattr(self._config, "MAX_CONTEXT_TOKENS", 4096)

        if not hasattr(self, "_index_manager") or self._index_manager is None:
            self._index_manager = IndexManager(
                vault_path=getattr(self._config, "VAULT_PATH", ""),
                api_key=getattr(self._config, "OPENAI_API_KEY", ""),
                embedding_model=getattr(
                    self._config, "EMBEDDING_MODEL", "text-embedding-ada-002"
                ),
            )
        storage = get_storage_backend(self._config)

        assembler = ContextAssembler(
            index_manager=self._index_manager,
            storage=storage,
            model=model_name,
            max_context_tokens=max_context_tokens,
        )
        ctx_result = assembler.assemble_context(
            query="",  # No search
            task="suggest_tags",
            top_k=0,
            extra_ids=[],
            user_prompt=f"Suggest tags for this note:\n\n{text}",
            min_tokens_for_reply=128,
        )
        prompt_to_send = ctx_result["context_block"]
        return self._backends["suggest_tags"].suggest_tags(prompt_to_send)

    def propose_links(self, text: str, note_names: List[str]) -> Tuple[str, int, int]:
        model_name = getattr(self._backends["propose_links"], "model", "gpt-3.5-turbo")
        max_context_tokens = getattr(self._config, "MAX_CONTEXT_TOKENS", 4096)

        if not hasattr(self, "_index_manager") or self._index_manager is None:
            self._index_manager = IndexManager(
                vault_path=getattr(self._config, "VAULT_PATH", ""),
                api_key=getattr(self._config, "OPENAI_API_KEY", ""),
                embedding_model=getattr(
                    self._config, "EMBEDDING_MODEL", "text-embedding-ada-002"
                ),
            )
        storage = get_storage_backend(self._config)

        assembler = ContextAssembler(
            index_manager=self._index_manager,
            storage=storage,
            model=model_name,
            max_context_tokens=max_context_tokens,
        )
        # You can add logic here to optionally inject short context for each note name if you want
        ctx_result = assembler.assemble_context(
            query="",  # No search
            task="propose_links",
            top_k=0,
            extra_ids=[],
            user_prompt=f"Suggest internal links for the following note, considering these possible note names:\n{', '.join(note_names)}\n\nNote:\n{text}",
            min_tokens_for_reply=256,
        )
        prompt_to_send = ctx_result["context_block"]
        return self._backends["propose_links"].propose_links(prompt_to_send, note_names)

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
