import logging

class Config:
    VAULT_PATH = r"C:\Users\Evan\Desktop\Ward_DND_Campaign"
    OPENAI_API_KEY = "REDACTED_KEY_REMOVED_FROM_HISTORY"
    LOG_PATH = r"C:\Users\Evan\Desktop\Ward_DND_Campaign\app.log"
    LOG_LEVEL = "INFO"

    @staticmethod
    def setup_logging():
        logging.basicConfig(
            filename=Config.LOG_PATH,
            level=logging.INFO,
            format="%(asctime)s %(levelname)s:%(message)s"
        )

def log_exception(message, exception):
    logging.error(f"{message} | Exception: {exception}")
