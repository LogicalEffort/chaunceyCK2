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

    for row in rows:
        cells = row.find_all(["td", "th"])
        row_data = []

        for cell in cells:
            row_data.append(cell.get_text(" ", strip=True))

        processed_rows.append(row_data)

    return processed_rows

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    url = "https://ck2.paradoxwikis.com/api.php?action=parse&pageid=40&prop=text&format=json"

    response = page.goto(url)
    data = response.json()

    html = data["parse"]["text"]["*"]

    soup = BeautifulSoup(html, "html.parser")

    toc = soup.find("div", id="toc")

    toc.decompose()

    #Removes the "edit" | "edit source" bits from headings
    edit_sections = soup.find_all("span", class_="mw-editsection")
    for section in edit_sections:
        section.decompose()

    elements = soup.find_all(["h2", "h3", "h4", "h5", "h6", "p", "ul", "ol", "table"])

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
        "pageid": 40,
        "title": "Warfare",
        "sections": sections
    }

    output_path = Path("data/content/processed/40.json")

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(processed_page, file, indent=4,ensure_ascii=False )

    browser.close()


