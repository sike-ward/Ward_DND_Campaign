import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from config import Config

# --- TOKEN COUNTING ---
import tiktoken

def count_tokens(text, model="gpt-3.5-turbo"):
    try:
        enc = tiktoken.encoding_for_model(model)
    except Exception:
        enc = tiktoken.get_encoding("cl100k_base")
    return len(enc.encode(text))

os.environ["OPENAI_API_KEY"] = Config.OPENAI_API_KEY

class LoreAI:
    def __init__(self, vault_path=None, api_key=None):
        self.vault_path = vault_path or Config.VAULT_PATH
        self.api_key = api_key or Config.OPENAI_API_KEY
        os.environ["OPENAI_API_KEY"] = self.api_key
        self.reload_data()

    def reload_data(self):
        documents = SimpleDirectoryReader(self.vault_path, recursive=True).load_data()
        self.index = VectorStoreIndex.from_documents(documents)
        retriever = self.index.as_retriever()
        self.engine = RetrieverQueryEngine(retriever=retriever)

    def query(self, question: str) -> str:
        return str(self.engine.query(question))

    # --- AI HELPERS ---

    def summarize(self, text, model="gpt-3.5-turbo"):
        prompt = f"Summarize this note in a single concise paragraph (no more than 4 sentences):\n\n{text}"
        prompt_tokens = count_tokens(prompt, model)
        response = self.query(prompt)
        response_tokens = count_tokens(str(response), model)
        return str(response), prompt_tokens, response_tokens

    def suggest_tags(self, text, model="gpt-3.5-turbo"):
        prompt = (
            "Suggest 3-7 useful tags (keywords or phrases) for this note, "
            "comma separated. Just give the tags:\n\n" + text
        )
        prompt_tokens = count_tokens(prompt, model)
        response = self.query(prompt)
        response_tokens = count_tokens(str(response), model)
        return str(response), prompt_tokens, response_tokens

    def propose_links(self, text, note_names, model="gpt-3.5-turbo"):
        prompt = (
            f"Based on the following note, suggest any likely Obsidian-style internal links "
            f"that should be added (choose only from this list of note names: {', '.join(note_names)}). "
            "Return just a list of matching note names:\n\n"
            f"{text}"
        )
        prompt_tokens = count_tokens(prompt, model)
        response = self.query(prompt)
        response_tokens = count_tokens(str(response), model)
        return str(response), prompt_tokens, response_tokens
