import json
from pathlib import Path


def validate_table(table_data, page_id, title, section_heading):
    rows = table_data["rows"]

    if not rows:
        return 0

    widths = {}

    for row in rows:
        width = len(row)

        if width not in widths:
            widths[width] = 0

        widths[width] += 1

    if len(widths) > 1:
        print(
            f"TABLE STRUCTURE | "
            f"Page: {title} ({page_id}) | "
            f"Section: {section_heading}"
        )

        print("Row withds:", widths)
        print()

        return 1
    
    return 0

processed_folder = Path("data/content/processedv2")

total_warnings = 0

for file_path in processed_folder.glob("*.json"):
    with open(file_path, "r", encoding="utf-8") as file:
        page_data = json.load(file)

    for section in page_data["sections"]:
        for content in section["content"]:
            if content["type"] == "table":
                total_warnings += validate_table(
                    content, 
                    page_data["pageid"],
                    page_data["title"],
                    section["heading"]
                )

print(f"Validation complete. Warnings: {total_warnings}")