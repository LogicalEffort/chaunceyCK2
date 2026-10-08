import json
from playwright.sync_api import sync_playwright

with open("data/content/raw/40.json", "r", encoding="utf-8") as file:
    warfare = json.load(file)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    response = page.request.post(
        "https://ck2.paradoxwikis.com/api.php",
        form={
            "action": "parse",
            "text": warfare["wikitext"],
            "title": warfare["title"],
            "prop": "text",
            "format": "json"
        }
    )

    #data = response.json()
    #print(data["parse"].keys())

    print("Status: ", response.status)
    print("Content type: ", response.headers.get("content-type"))
    print(response.text()[:1000])

    browser.close()