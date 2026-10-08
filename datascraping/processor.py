from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from copy import copy
import json
from pathlib import Path

def process_list(list_element):
    processed_items = []

    items = list_element.find_all("li", recursive=False)

    for item in items:
        nested_list = item.find(["ul", "ol"], recursive=False)

        item_copy = copy(item)

        for child_list in item_copy.find_all(["ul", "ol"], recursive=False):
            child_list.decompose()

        item_text = item_copy.get_text(" ", strip=True)

        item_data = {
            "text": item_text,
            "children": []
        }

        if nested_list is not None:
            item_data["children"] = process_list(nested_list)

        processed_items.append(item_data)

    return processed_items

def process_table(table_element):
    rows = table_element.find_all("tr")
    processed_rows = []

    active_rowspans = []

    for row in rows:
        row_data = []

        # Add cells carried over from previous rowspans
        for span in active_rowspans:
            row_data.append(span["text"])
            span["rows_left"] -= 1

        # Remove finished rowspans
        active_rowspans = [
            span for span in active_rowspans
            if span["rows_left"] > 0
        ]

        cells = row.find_all(["td", "th"], recursive=False)

        for cell in cells:
            cell_text = cell.get_text(" ", strip=True)
            row_data.append(cell_text)

            rowspan = int(cell.get("rowspan", 1))

            if rowspan > 1:
                active_rowspans.append({
                    "text": cell_text,
                    "rows_left": rowspan - 1
                })

        processed_rows.append(row_data)

    return processed_rows

def process_page(raw_file, page):
    try:
        # Read page info from raw archive
        with open(raw_file, "r", encoding="utf-8") as file:
            raw_data = json.load(file)

        page_id = raw_data["pageid"]
        title = raw_data["title"]

        output_path = Path(f"data/content/processed/{page_id}.json")

        if output_path.exists():
            print("Already processed ", title)
            return

        url = f"https://ck2.paradoxwikis.com/api.php?action=parse&pageid={page_id}&prop=text&format=json"

        response = page.goto(url)
        data = response.json()

        html = data["parse"]["text"]["*"]

        soup = BeautifulSoup(html, "html.parser")

        # Remove generated table of contents
        toc = soup.find("div", id="toc")

        if toc is not None:
            toc.decompose()

        # Remove wiki metadata/help box if present
        help_texts = soup.select("div.eu4box.metadata")

        for help_text in help_texts:
            help_text.decompose()

        # Remove "[edit | edit source]" controls
        edit_sections = soup.find_all("span", class_="mw-editsection")

        for section in edit_sections:
            section.decompose()

        # Get useful content in document order
        elements = soup.find_all([
                "h2", "h3", "h4", "h5", "h6",
                "p", "ul", "ol", "table"
            ])

        sections = []

        current_section = {
            "heading": "Introduction",
            "level": 1,
            "content": []
        }

        sections.append(current_section)

        for element in elements:
            if element.name in ["h2", "h3", "h4", "h5", "h6"]:
        
                current_section = {
                    "heading": element.get_text(" ", strip=True),
                    "level": int(element.name[1]),
                    "content": []
                }
                
                sections.append(current_section)
        
            elif element.name == "p":
                paragraph = {
                    "type": "paragraph",
                    "text": element.get_text(" ", strip=True)
                }
        
                current_section["content"].append(paragraph)
        
            elif element.name in ["ul", "ol"]:
                if element.find_parent(["ul", "ol"]) is not None:
                    continue
        
                list_data = {
                    "type": "list",
                    "list_type": element.name,
                    "items": process_list(element)
                }
        
                current_section["content"].append(list_data)

            elif element.name == "table":
                table_data = {
                    "type": "table",
                    "rows": process_table(element)
                }
        
                current_section["content"].append(table_data)

        processed_page = {
            "pageid": page_id,
            "title": title,
            "sections": sections
        }

        with open(output_path, "w", encoding="utf-8") as file:
            json.dump(processed_page, file, indent=4, ensure_ascii=False)

        print("Processed:", title)

    except Exception as e:
        print("ERROR processing:", raw_file.name)
        print("Error:", e)


raw_folder = Path("data/content/raw")
processed_folder = Path("data/content/processed")

processed_folder.mkdir(parents=True, exist_ok=True)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    raw_files = sorted(
        raw_folder.glob("*.json"),
        key=lambda file: int(file.stem)
    )

    for raw_file in raw_files:
        process_page(raw_file, page)

    browser.close()


