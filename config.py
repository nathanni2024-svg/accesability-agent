import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("APP_DATA_DIR", BASE_DIR / "data")).resolve()
GRAPH_DIR = Path(os.getenv("GRAPH_OUTPUT_DIR", DATA_DIR / "generated_graphs")).resolve()
MESSAGES_DIR = Path(os.getenv("SORTED_MESSAGES_DIR", DATA_DIR / "sorted_messages")).resolve()
SQLITE_DB_PATH = Path(os.getenv("AI_BRAIN_DB_PATH", DATA_DIR / "ai_brain.db")).resolve()


def ensure_app_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_DIR.mkdir(parents=True, exist_ok=True)
    MESSAGES_DIR.mkdir(parents=True, exist_ok=True)
