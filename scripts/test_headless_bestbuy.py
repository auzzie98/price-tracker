"""Headless browser test for Best Buy product page.

Test only. Saves no observation to the database.

Opens Chromium in headless mode with a normal desktop user agent,
opens the Best Buy product page once, waits for it to load, then
reports the page title, whether a CAPTCHA or Cloudflare check appeared,
and whether the price text 479 is visible on the page.
Results are saved to headless_test_result.txt in the repo root.
"""

from __future__ import annotations

from playwright.sync_api import sync_playwright, Error
import os

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULT_FILE = os.path.join(REPO_ROOT, "headless_test_result.txt")

URL = (
    "https://www.bestbuy.com/product/"
    "amd-ryzen-7-9800x3d-8-core-16-thread-4-7-ghz-5-2-ghz-max-boost-"
    "socket-am5-pci-express-5-0-unlocked-desktop-processor-silver/"
    "JXKQHH5XSR"
)


def main() -> None:
    title = ""
    captcha_found = False
    price_visible = False

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--disable-http2"])
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/159.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        print(f"Opening: {URL}")
        try:
            page.goto(URL, wait_until="networkidle", timeout=30000)
            title = page.title()
            print(f"Page title: {title}")

            body_text = page.locator("body").inner_text()
            lower_body = body_text.lower()

            captcha_keywords = ["captcha", "cloudflare", "just a moment", "verify you are human"]
            captcha_found = any(k in lower_body for k in captcha_keywords)
            print(f"CAPTCHA/Cloudflare detected: {captcha_found}")

            price_visible = "479" in body_text
            print(f"Price 479 visible on page: {price_visible}")
        except Error as e:
            print(f"Navigation error: {e}")
            title = "NAVIGATION_ERROR"

    # Save results to file (always write, even on error)
    with open(RESULT_FILE, "w") as f:
        f.write(f"{title}\n")
        f.write(f"{'yes' if captcha_found else 'no'}\n")
        f.write(f"{'yes' if price_visible else 'no'}\n")
        f.write(f"{URL}\n")

    print(f"Results saved to {RESULT_FILE}")

    # Don't close browser if we never navigated
    try:
        browser.close()
    except Exception:
        pass


if __name__ == "__main__":
    main()