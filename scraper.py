import sys
import json
from playwright.sync_api import sync_playwright

def run_scraper(query: str):
    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )

        page = context.new_page()
        page.goto(f"https://www.google.com/search?q={query}", timeout=15000)

        try:
            page.get_by_role("button", name="Přijmout vše").click(timeout=3000)
        except:
            try:
                page.get_by_role("button", name="Alle akzeptieren").click(timeout=3000)
            except:
                pass

        page.mouse.move(200, 200)
        page.mouse.wheel(0, 300)

        try:
            page.wait_for_selector("h3", timeout=7000)
            headers = page.locator("h3").all()

            for h in headers:
                try:
                    link = h.evaluate("el => el.closest('a')?.href")
                    title = h.inner_text()
                    if link and "google.com" not in link:
                        results.append({"title": title, "link": link})
                except:
                    continue
        except:
            pass

        browser.close()

    return results

if __name__ == "__main__":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    query = sys.argv[1]
    results = run_scraper(query)

    with open("results.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(json.dumps(results, ensure_ascii=False, indent=2))