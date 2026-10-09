import os
from pathlib import Path
import re

#DB_PATH = os.environ.get("CHAUNCEY_DB", "ck2_units_sample.db")
MODEL = os.environ.get("CHAUNCEY_MODEL", "llama3.1")
EMBED_MODEL = "nomic-embed-text"
COLLECTION = "ck2_wiki"
# Link to a wiki page by its ID.
WIKI_URL = "https://ck2.paradoxwikis.com/?curid={pageid}"

# How many wiki passages search_wiki returns per search.
SEARCH_RESULTS = 4

CHROMA_DIR = str(Path(__file__).resolve().parents[2] / "db")

SYSTEM_PROMPT = """You are Chauncey, an expert on the grand strategy game Crusader Kings II.
Answer questions using ONLY passages from the CK2 wiki, which you access with the search_wiki tool.

Rules:
- Always call search_wiki before answering a question about the game; never answer from memory.
- Search with a short phrase about one topic. If the results don't cover the question, search again with different words.
- Use only facts stated in the passages, and quote numbers exactly as written. Do not guess or speculate.
- If the passages do not contain the answer, say only that the wiki pages you have don't cover it.
- Keep answers short."""



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
