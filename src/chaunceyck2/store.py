from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_ollama import OllamaEmbeddings

from chaunceyck2.constants import CHROMA_DIR, COLLECTION, EMBED_MODEL


@lru_cache(maxsize=1)
def get_store() -> Chroma:
    return Chroma(
        collection_name=COLLECTION,
        persist_directory=CHROMA_DIR,
        embedding_function=OllamaEmbeddings(model=EMBED_MODEL),
        collection_metadata={"hnsw:space": "cosine"},
    )


def replace_page(store: Chroma, page_id: int, docs: list[Document]) -> None:
    # Clear the page's old chunks first, so none are left over if it now has fewer.
    store.delete(where={"page_id": page_id})
    store.add_documents(docs)
