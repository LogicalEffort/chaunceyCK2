import re
import sys
import json


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

def render_block(block: dict) -> str:
    if block["type"] == "paragraph":
        return tidy(block["text"])
    if block["type"] == "list":
        return render_list(block["items"], ordered=block["list_type"] == "ol")
    if block["type"] == "table":
        return render_table(block["rows"])
    raise ValueError(f"Unknown block type: {block['type']}")

######Temporary function to test
if __name__ == "__main__":
    page = json.load(open(sys.argv[1], encoding="utf-8"))
    for section in page["sections"]:
        print(f"\n=== {section['heading']} (level {section['level']})")
        for block in section["content"]:
            print(render_block(block), end="\n\n")

