import os
from pathlib import Path
import re

DB_PATH = os.environ.get("CHAUNCEY_DB", "ck2_units_sample.db")
MODEL = os.environ.get("CHAUNCEY_MODEL", "llama3.1")
EMBED_MODEL = "nomic-embed-text"
COLLECTION = "ck2_wiki"

CHROMA_DIR = str(Path(__file__).resolve().parents[2] / "db")

SYSTEM_PROMPT = """You are Chauncey, an expert on the grand strategy game Crusader Kings II.
Answer questions using ONLY data from the CK2 SQLite database, which you access with tools:
1. run_sql to fetch the facts

Rules:
- Always query the database before answering a factual question; never guess stats.
- In CK2, combat has three phases: skirmish, melee, pursue. Units have an attack and defense per phase.
- If the database does not contain the answer, say so plainly.
- Keep answers short and cite the exact numbers you retrieved."""


# Soft limit: a section longer than this is split into several chunks, between blocks.
MAX_CHUNK_CHARS = 1500
# When a section is split, repeat the previous chunk's last unit at the start of
# the next chunk if it's no longer than this. 0 turns overlap off.
OVERLAP_CHARS = 400

# A table with any cell longer than this gets one chunk per row.
LONG_CELL_CHARS = 100

# Maintenance banner at the top of some pages:
# "Please help with verifying or updating ... last verified for version 2.8."
BANNER_RE = re.compile(r"^Please help with verifying or updating")
VERSION_RE = re.compile(r"verified for version (\d+(?:\.\d+)*)")
