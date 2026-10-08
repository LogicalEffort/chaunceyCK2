from langchain_core.tools import tool

from chaunceyck2.constants import SEARCH_RESULTS
from chaunceyck2.store import get_store


@tool(
    "search_wiki",
    description="Search the Crusader Kings II wiki. Takes a short search phrase about one topic "
                "and returns the most relevant wiki passages.",
)
def search_wiki(query: str) -> str:
    docs = get_store().similarity_search(query, k=SEARCH_RESULTS)
    if not docs:
        return "No wiki passages found."
    passages = []
    for doc in docs:
        version = doc.metadata.get("verified_version")
        note = f" (last verified for game version {version})" if version else ""
        passages.append(f"Source: {doc.metadata['url']}{note}\n{doc.page_content}")
    return "\n\n---\n\n".join(passages)
