import re
import sys
import json
from chaunceyck2.constants import *
from chaunceyck2.store import get_store, replace_page
from langchain_core.documents import Document


def tidy(text: str) -> str:
    text = re.sub(r"\s+([,.;:)])", r"\1", text)   # "Morale ;" -> "Morale;"
    return re.sub(r"\(\s+", "(", text)            # "( Zun lodge)" -> "(Zun lodge)"


def render_list(items: list[dict], ordered: bool = False, depth: int = 0) -> str:
    lines = []
    for n, item in enumerate(items, start=1):
        marker = f"{n}." if ordered else "-"
        lines.append(f"{'  ' * depth}{marker} {tidy(item['text'])}")
        if item["children"]:
            lines.append(render_list(item["children"], ordered, depth + 1))
    return "\n".join(lines)


def render_table(rows: list[list[str]]) -> str:
    header, *body = rows
    lines = []
    for row in body:
        cells = [f"{name} {value}" for name, value in zip(header[1:], row[1:]) if value]
        lines.append(f"{row[0]}: {'; '.join(cells) or 'no modifiers'}")
    return "\n".join(lines)

def is_record_table(rows: list[list[str]]) -> bool:
    # One entity per row with descriptive cells, e.g. the bloodline tables.
    return any(len(cell) > LONG_CELL_CHARS for row in rows[1:] for cell in row)


def render_rows(rows: list[list[str]]) -> list[str]:
    # One labelled record per row: "Name: Blood of Caradog\nFounder: ..."
    header, *body = rows
    records = []
    for row in body:
        if len(row) != len(header):
            # A merged cell was lost in the export, so the columns can't be trusted.
            print(f"warning: row has {len(row)} cells, header has {len(header)}: {header}", file=sys.stderr)
            records.append(" | ".join(tidy(cell) for cell in row if cell))
            continue
        records.append("\n".join(
            f"{name}: {tidy(value)}" if name else tidy(value)
            for name, value in zip(header, row) if value
        ))
    return records


def render_block(block: dict) -> str:
    if block["type"] == "paragraph":
        return tidy(block["text"])
    if block["type"] == "list":
        return render_list(block["items"], ordered=block["list_type"] == "ol")
    if block["type"] == "table":
        return render_table(block["rows"])
    raise ValueError(f"Unknown block type: {block['type']}")

def pack_blocks(blocks: list[dict]) -> list[str]:
    # Join a lead-in paragraph ("Sources of troops include:") to the block after it.
    units = []
    glue = False
    for block in blocks:
        text = render_block(block)
        if glue:
            units[-1] += "\n" + text
        else:
            units.append(text)
        glue = block["type"] == "paragraph" and text.endswith(":")

    # Fill each chunk until the next unit would push it past the limit.
    chunks = []
    prev_unit = None
    for unit in units:
        if chunks and len(chunks[-1]) + len(unit) <= MAX_CHUNK_CHARS:
            chunks[-1] += "\n\n" + unit
        elif prev_unit and len(prev_unit) <= OVERLAP_CHARS:
            chunks.append(prev_unit + "\n\n" + unit)
        else:
            chunks.append(unit)
        prev_unit = unit
    return chunks

def chunk_section(blocks: list[dict]) -> list[str]:
    chunks = []
    run = []   # consecutive blocks to pack together
    for block in blocks:
        if block["type"] == "table" and is_record_table(block["rows"]):
            chunks += pack_blocks(run)
            run = []
            chunks += render_rows(block["rows"])
        else:
            run.append(block)
    return chunks + pack_blocks(run)


def chunk_page(page: dict) -> tuple[list[dict], str | None]:
    """Returns the page's chunks and the game version from its banner, if it has one."""
    title = page["title"]
    version = None
    chunks = []
    stack = []   # headings of the sections we're currently inside, as (level, heading)

    for section_index, section in enumerate(page["sections"]):
        level, heading = section["level"], section["heading"]

        # Leave any sections at this level or deeper, then enter this one.
        while stack and stack[-1][0] >= level:
            stack.pop()
        stack.append((level, heading))
        heading_path = " > ".join([title] + [h for _, h in stack])
        # The level-1 lead section isn't a parent of the sections after it.
        if level == 1:
            stack.clear()

        blocks = []
        for block in section["content"]:
            if block["type"] == "paragraph" and BANNER_RE.match(block["text"]):
                match = VERSION_RE.search(block["text"])
                version = match.group(1) if match else version
                continue
            blocks.append(block)

        for chunk_index, body in enumerate(chunk_section(blocks)):
            chunks.append({
                "section_index": section_index,
                "chunk_index": chunk_index,
                "heading_path": heading_path,
                "text": f"{heading_path}\n\n{body}",
            })
    return chunks, version

def page_documents(page: dict) -> list[Document]:
    """Returns the page's chunks as Documents, ready to store."""
    chunks, version = chunk_page(page)
    page_id = page["pageid"]

    # Facts shared by every chunk on the page.
    page_metadata = {
        "page_id": page_id,
        "title": page["title"],
        "url": WIKI_URL.format(pageid=page_id),
    }
    if version:
        page_metadata["verified_version"] = version

    return [
        Document(
            id=f"{page_id}:{chunk['section_index']}:{chunk['chunk_index']}",
            page_content=chunk["text"],
            metadata={**page_metadata, "heading_path": chunk["heading_path"]},
        )
        for chunk in chunks
    ]


######Temporary function to test
if __name__ == "__main__":
    store = get_store()
    for path in sys.argv[1:]:
        page = json.load(open(path, encoding="utf-8"))
        docs = page_documents(page)
        replace_page(store, page["pageid"], docs)
        print(f"{path}: stored '{page['title']}' as {len(docs)} chunks")




