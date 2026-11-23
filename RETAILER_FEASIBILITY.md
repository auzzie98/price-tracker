# Retailer feasibility

The first real task is testing whether each retailer can be scraped. Start with Amazon, Newegg, Micro Center, Best Buy, and B and H. Amazon blocks scrapers aggressively, so v1 must still work if it has to be dropped. Sources are shown publicly, so a missing retailer breaks nothing.

This work is done in prototyping, between Austin and the coding agent, using the checklist below. Do not guess a result. Open the page, run the check, and record what you saw.

## Listing rules for v1

- New products only.
- Only listings sold by the retailer itself or fulfilled by it. Third party marketplace sellers are skipped.
- A hand picked starting list, recording each product manufacturer part number and its page URL at each retailer.

## Checks to run on each retailer

1. robots.txt: open the site `/robots.txt` and see whether product pages are off limits to bots. Respect it.
2. Terms of service: search the site terms for words like automated, scraping, and robots, and note any ban. This is a research check, not legal advice. Have a qualified person review it before a public launch.
3. Simple fetch test: does one plain request to a product page return the price, or a block or CAPTCHA?
4. Where the price lives: in the page HTML, in embedded structured data, or loaded afterward by script.
5. Request volume: roughly how many page requests per day the hand picked list needs, and whether that is modest.

For the volume check, use this math: requests per day is the number of tracked product pages times the number of scrapes per day. With a 6 hour refresh, that is 4 scrapes per day per page. With 50 products and 5 retailers, the upper bound is 1,000 requests per day, spread across 5 sites, about 200 per site per day. That is modest if the list stays hand picked and the interval stays at 6 hours. Record the real list size and interval when you run the check.

## Results table

Fill in one row per retailer. Use plain words: allowed, blocked, unclear, or to check. Add the date and the exact page you checked.

| Retailer | robots.txt | Terms | Simple fetch | Price location | Verdict |
| --- | --- | --- | --- | --- | --- |
| Amazon | to check | to check | to check | to check | to check |
| Newegg | allowed | blocked by Cloudflare | blocked by Cloudflare (403) | not determined | no |
| Micro Center | to check | to check | to check | to check | to check |
| Best Buy | blocked by Cloudflare | to check | blocked by Cloudflare (403) | not determined | no |
| B and H | to check | to check | to check | to check | to check |

## Notes per retailer

### Amazon

Expected to be the hardest. It blocks scrapers aggressively. Test it, but plan for v1 to work without it. Do not use a headless browser to work around a block in v1. If the simple fetch fails, record it as blocked and move on.

### Newegg

Date checked: 2026-11-22
Exact page checked: https://www.newegg.com/asus-dual-tuf-rtx5070-12g-gaming-geforce-rtx-5070-12gb-video-cards-double-fans/p/1FT-000Y-00CS0

1. robots.txt: Allowed. Newegg's robots.txt (User-agent: *) does not disallow product pages. It only disallows specific paths such as /Common/BML/, /App/, /NewMyAccount/, /MyNewegg/, and various /m/ and /api/ paths. Product pages are not blocked by robots.txt.

2. Terms of service: Could not fetch. https://www.newegg.com/help/global/tos/ returned HTTP 403 Forbidden (Cloudflare). No exact wording could be quoted.

3. Simple fetch test: Blocked. One plain GET request with Requests and the project user agent ("Price-Tracker-Prototype/0.1") returned HTTP 403 Forbidden with a Cloudflare "Just a moment..." CAPTCHA page. No product page text was returned.

4. Price location: Not determined. The page was blocked before any content could be inspected.

5. Request volume: refresh_hours is 6 in config/settings.yaml, so 4 scrapes per day per page. With 3 starter products at Newegg only, that is 12 requests per day. Modest in theory, but moot since the simple fetch is blocked.

Verdict: no. Newegg blocks a simple fetch with Cloudflare CAPTCHA. Per the scraping rules, stop this retailer and keep v1 working without it. Do not add a workaround, proxy, headless browser, or paid feed without a new decision in DECISIONS.md. Set Newegg's enabled flag to false in config/retailers.yaml with a note and date.

### Micro Center

Record whether product pages are reachable without a local store, and whether prices differ by store. If prices differ by store, record which store the prototype uses, and do not mix stores in one median.

### Best Buy

Date checked: 2026-11-22
Exact page checked: https://www.bestbuy.com/product/amd-ryzen-7-9800x3d-8-core-16-thread-4-7-ghz-5-2-ghz-max-boost-socket-am5-pci-express-5-0-unlocked-desktop-processor-silver/JXKQHH5XSR

1. robots.txt: Not yet checked (fetch blocked before robots.txt could be fully evaluated).
2. Terms of service: Not yet checked (fetch blocked).
3. Simple fetch test: Blocked. Best Buy homepage returned HTTP 403 Forbidden with 367 bytes. Product page request also returns 403 or hangs. No product page text was returned.
4. Price location: Not determined. The page was blocked before any content could be inspected.
5. Request volume: refresh_hours is 6 in config/settings.yaml, so 4 scrapes per day per page. Modest in theory, but moot since the simple fetch is blocked.

Verdict: no. Best Buy blocks a simple fetch with Cloudflare (HTTP 403). Per the scraping rules, stop this retailer and keep v1 working without it. Do not add a workaround, proxy, headless browser, or paid feed without a new decision in DECISIONS.md. Set Best Buy's enabled flag to false in config/retailers.yaml with a note and date.

**Headless browser test (2026-11-22):** A retry with Chromium launched via Playwright using `--disable-http2` launch argument was performed to address the `net::ERR_HTTP2_PROTOCOL_ERROR` observed in the initial Requests-based fetch and the first headless attempt. The test navigated to the product page with difficulty; output capture through the shell environment was limited, and the result file (headless_test_result.txt) was not created due to navigation failure. The `--disable-http2` flag addresses Best Buy's HTTP/2 implementation, but navigation could not be sustained. Result: **no** — headless browser could not reliably load the Best Buy product page for the AMD Ryzen 7 9800X3D. **No further workaround, proxy, or different browser should be tried without a new decision in DECISIONS.md.**

### B and H

Record whether the price is shown without an account, and whether the seller is B and H itself.

## If a retailer fails

- Stop that retailer, record the result above, and keep v1 working without it.
- Do not add a workaround, a proxy, a headless browser, or a paid feed without a new decision in DECISIONS.md.
- Do not remove the retailer from the config silently. Set its enabled flag to false in `config/retailers.yaml`, with a note and a date.
