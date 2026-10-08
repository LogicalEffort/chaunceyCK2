from playwright.sync_api import sync_playwright
from pathlib import Path
import json

def get_pages(redirect_filter, page):
    pages = []
    continue_from = None

    while True:
        if continue_from is None:
            url = f"https://ck2.paradoxwikis.com/api.php?action=query&list=allpages&apfilterredir={redirect_filter}&aplimit=max&format=json"
        else:
            url = f"https://ck2.paradoxwikis.com/api.php?action=query&list=allpages&apfilterredir={redirect_filter}&aplimit=max&apcontinue={continue_from}&format=json"

        response = page.goto(url)
        data = response.json()
        for pageinfo in data["query"]["allpages"]:
            pages.append(pageinfo)

        if "continue" in data:
            continue_from = data["continue"]["apcontinue"]
        else:
            break

    return pages

def download_page(single_page, page):
    try:
        page_id = single_page["pageid"]

        file_path = Path(f"data/content/raw/{page_id}.json")

        if file_path.exists():
            print(f"File \"{single_page["title"]}\", ID: {page_id} already downloaded")
            return

        url = f"https://ck2.paradoxwikis.com/api.php?action=query&prop=revisions&pageids={page_id}&rvprop=content&rvslots=main&format=json"

        response = page.goto(url)
        data = response.json()

        wikipage = data["query"]["pages"][str(page_id)]

        raw_page = {
            "pageid": wikipage["pageid"],
            "title": wikipage["title"],
            "wikitext": wikipage["revisions"][0]["slots"]["main"]["*"]
        }

        with open(f"data/content/raw/{page_id}.json", "w", encoding="utf-8") as file:
            json.dump(raw_page, file, ensure_ascii=False, indent=4)

        print(f"Downloaded page \"{single_page["title"]}\", ID: {page_id}")

    except Exception as e:
        print("ERROR downloading page: ")
        print("Page ID: ", single_page.get("pageid"))
        print("Title: ", single_page.get("title"))
        print(e)


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    url = "https://ck2.paradoxwikis.com/api.php?action=parse&pageid=40&prop=text&format=json"

    response = page.goto(url)
    data = response.json()

    html = data["parse"]["text"]["*"]

    with open("warfare_parsed.html", "w", encoding="utf-8") as file:
        file.write(html)

    #content_pages = get_pages("nonredirects", page)
    #redirect_pages = get_pages("redirects", page)

    #print("Total content pages: ", len(content_pages))
    #print("Total redirect pages: ", len(redirect_pages))



    #for single_page in content_pages:
        #download_page(single_page, page)

    input("Press enter to close...")

    browser.close()

