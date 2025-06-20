import csv
import os
from datetime import datetime

# Update prices as needed. Default rates are for illustration only.
OPENAI_PRICES = {
    "gpt-3.5-turbo": 0.0015 / 1000,  # $0.0015 per 1K tokens
    "gpt-4": 0.03 / 1000,  # $0.03 per 1K tokens
    # Add other models as needed
}

LOG_PATH = os.path.join(os.path.dirname(__file__), "ai_usage_log.csv")


def estimate_cost(model, prompt_tokens, completion_tokens):
    """Estimate OpenAI API call cost in USD."""
    rate = OPENAI_PRICES.get(model, 0.002 / 1000)  # Default rate if unknown
    return rate * (prompt_tokens + completion_tokens)


def log_api_call(
    model,
    task,
    prompt_tokens,
    completion_tokens,
    cost,
    success=True,
    error_msg=None,
    prompt=None,
):
    """Append an API call record to the CSV log (with optional prompt text)."""
    exists = os.path.exists(LOG_PATH)
    with open(LOG_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not exists:
            writer.writerow(
                [
                    "timestamp",
                    "model",
                    "task",
                    "prompt_tokens",
                    "completion_tokens",
                    "total_tokens",
                    "cost_usd",
                    "success",
                    "error_msg",
                    "prompt",
                ]
            )
        writer.writerow(
            [
                datetime.now().isoformat(),
                model,
                task,
                prompt_tokens,
                completion_tokens,
                prompt_tokens + completion_tokens,
                round(cost, 6),
                success,
                error_msg or "",
                prompt or "",
            ]
        )


def read_logs(n=20):
    """Read the last n log records as a list of dicts (most recent last)."""
    if not os.path.exists(LOG_PATH):
        return []
    with open(LOG_PATH, "r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
        return rows[-n:] if n else rows
