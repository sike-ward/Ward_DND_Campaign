from typing import Any, Literal, Optional

ModelName = Literal["gpt-3.5", "gpt-4", "claude-2", "local-llm"]


class ModelRouter:
    """Central model dispatch and configuration manager."""

    def __init__(self, model: ModelName = "gpt-3.5", api_key: Optional[str] = None):
        self.model = model
        self.api_key = api_key
        self._client = self._load_client(model)

    def _load_client(self, model: str) -> Any:
        """Dynamically load the correct model client backend."""
        if model.startswith("gpt-"):
            return self._load_openai()
        elif model.startswith("claude"):
            return self._load_anthropic()
        elif model == "local-llm":
            return self._load_local()
        else:
            raise ValueError(f"Unsupported model: {model}")

    def _load_openai(self):
        import openai

        openai.api_key = self.api_key
        return openai

    def _load_anthropic(self):
        import anthropic

        return anthropic.Anthropic(api_key=self.api_key)

    def _load_local(self):
        # placeholder — you could plug in llama.cpp, ollama, etc.
        raise NotImplementedError("Local model backend not yet implemented")

    def query(self, prompt: str, system: Optional[str] = None) -> str:
        """Send prompt to the active model and return the response as a string."""
        if self.model.startswith("gpt-"):
            return self._query_openai(prompt, system)
        elif self.model.startswith("claude"):
            return self._query_anthropic(prompt, system)
        else:
            raise NotImplementedError("Only GPT and Claude models supported in v0.")

    def _query_openai(self, prompt: str, system: Optional[str]) -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        completion = self._client.ChatCompletion.create(
            model=self.model,
            messages=messages,
        )
        return completion.choices[0].message.content.strip()

    def _query_anthropic(self, prompt: str, system: Optional[str]) -> str:
        return (
            self._client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=0.7,
                system=system or "",
                messages=[{"role": "user", "content": prompt}],
            )
            .content[0]
            .text.strip()
        )
