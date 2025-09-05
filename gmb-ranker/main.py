from playwright.sync_api import sync_playwright
import sys

def run_simulation():
    try:
        with sync_playwright() as p:
            # Use --no-sandbox for containerized environments
            browser = p.chromium.launch(headless=True, args=['--no-sandbox'])
            page = browser.new_page()
            page.goto("https://www.google.com")

            search_bar = page.query_selector('textarea[name="q"]')
            if search_bar:
                search_bar.fill("Google My Business")
                page.press('textarea[name="q"]', 'Enter')
                print("Search submitted.")
            else:
                print("Search bar not found.")
                return

            page.wait_for_load_state('networkidle')
            print("Navigated to search results.")

            page.screenshot(path="screenshot.png")
            print("Screenshot taken.")

            browser.close()
            print("Browser closed.")
            # Signal success
            with open("success.txt", "w") as f:
                f.write("Success")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_simulation()
