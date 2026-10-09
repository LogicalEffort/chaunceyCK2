# Chauncey - A Crusader Kings 2 Knowledge bot

Chauncey answers questions about Crusader Kings II from pages of the
[CK2 wiki](https://ck2.paradoxwikis.com). It runs locally: an Ollama chat model
searches a ChromaDB vector store of wiki passages and answers only from what it finds.

Chauncey currently runs as a console program, with all wiki pages ingested.

## How it works

1. **Scrape**: scripts in `datascraping/` fetch a wiki page and save it as structured JSON
   (sections containing paragraphs, lists and tables).
2. **Ingest**: `dataparser.py` turns each page into text chunks, embeds them with
   `nomic-embed-text` and stores them in ChromaDB (the `db/` folder).
3. **Answer**: a LangChain agent on `llama3.1` calls the `search_wiki` tool to retrieve the
   closest passages, then answers from them. It remembers earlier questions within a session.

## Requirements

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [Ollama](https://ollama.com), running locally

## Setup

```
uv sync
ollama pull llama3.1
ollama pull nomic-embed-text
```

## Build the knowledge base

The `db/` folder is not tracked in git. Build it from the processed JSON pages:

```
uv run python -m chaunceyck2.dataparser datascraping/data/content/processed/*.json
```

Each page prints a line such as `stored 'Warfare' as 38 chunks`. Re-running the command
replaces a page's chunks; it does not duplicate them.

## Run

Start an interactive session:

```
uv run python -m chaunceyck2.chauncey
```

Or ask a single question:

```
uv run python -m chaunceyck2.chauncey "What happens if I break a truce?"
```

The first answer is slow while Ollama loads the models.

## Configuration

Settings live in `src/chaunceyck2/constants.py`.

| Setting | Default | Purpose |
|---|---|---|
| `MODEL` | `llama3.1` | Chat model. Override with the `CHAUNCEY_MODEL` environment variable. |
| `EMBED_MODEL` | `nomic-embed-text` | Embedding model. Changing it requires deleting `db/` and re-ingesting. |
| `SEARCH_RESULTS` | `4` | Passages returned per search. |
| `MAX_CHUNK_CHARS` | `1500` | Soft size limit for a chunk. |
| `OVERLAP_CHARS` | `400` | Largest block repeated between consecutive chunks of a section. `0` turns overlap off. |
| `LONG_CELL_CHARS` | `100` | A table with a cell longer than this is chunked one row at a time. |

## Project layout

```
src/chaunceyck2/
  chauncey.py      Console entry point
  agent.py         Builds the agent (model, tool, conversation memory)
  agent_tools.py   The search_wiki tool
  store.py         Creates the ChromaDB store; replaces a page's chunks
  dataparser.py    JSON page -> chunks -> Documents -> store
  constants.py     Settings and the system prompt
datascraping/
  scraper.py       Downloads pages from the wiki API
  processor.py     Converts a page's HTML into the processed JSON format
  data/content/processed/   Processed pages, one JSON file per wiki page ID
```

## Scraping more pages

The scraping scripts drive a visible Chromium browser through Playwright, because the wiki
does not answer plain HTTP requests. Their dependencies are not in `pyproject.toml`:

```
uv pip install playwright beautifulsoup4
uv run playwright install chromium
```

Run them from inside `datascraping/`, since their paths are relative to that folder.
`processor.py` currently has its page ID, title and output file hardcoded, so edit those
for each page.

## Known limitations

- **List-everything questions**: a question such as "which bloodlines are matrilineal?" needs
  every matching row, but a search returns only the closest few passages.
- **Table rows**: tables with long cells are chunked one row at a time, which can return
  disconnected fragments for tables that only make sense as a whole.
- **Merged table cells**: the processor drops them, so some rows lose their first column.
- **Memory**: conversation history is kept in the running process and is lost on exit.
- **Sources**: answers do not include links to the wiki pages they came from.
