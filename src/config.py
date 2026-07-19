"""
Configuration module.
Loads environment variables from .env and exposes centralized settings.
"""

import os
from dotenv import load_dotenv

# Load variables from .env file in the project root
load_dotenv()

# ── LLM Configuration ──────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")  # Switch to "gpt-4o" if desired

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL_NAME = os.getenv("GEMINI_MODEL_NAME", "gemini-2.5-flash")

# ── Paths ───────────────────────────────────────────────────────────────────────
CHROMA_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "chroma_db")
DATA_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sports_facts.json")

# ── Startup Validation ──────────────────────────────────────────────────────────
if (not OPENAI_API_KEY or OPENAI_API_KEY == "your-api-key-here") and not GEMINI_API_KEY:
    print(
        "\n[WARNING] Neither OPENAI_API_KEY nor GEMINI_API_KEY is set in your .env file.\n"
        "   -> Please add your API keys to the .env file in the project root.\n"
        "   -> Example: OPENAI_API_KEY=sk-proj-...\n"
        "   -> Example: GEMINI_API_KEY=AIzaSy...\n"
    )
