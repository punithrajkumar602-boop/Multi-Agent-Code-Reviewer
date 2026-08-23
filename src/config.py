"""
Central configuration for the Multi-Agent Code Reviewer.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

LLM_MODEL = "openai/gpt-oss-20b"

# Max file size (in characters) sent to the LLM per file, to control
# token usage on very large diffs
MAX_FILE_CHARS = 6000

if not GROQ_API_KEY:
    print("[WARNING] GROQ_API_KEY not set. Add it to your .env file before running.")
if not GITHUB_TOKEN:
    print("[INFO] GITHUB_TOKEN not set. Only public repos can be reviewed, and rate limits will be low.")
