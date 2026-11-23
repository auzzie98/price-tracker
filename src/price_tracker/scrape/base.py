"""Shared scraper behavior. Task 6 creates the real code.

Same input for every scraper: a SKU and a product page URL.
Same output: an observation, timestamp, SKU, retailer, price,
in stock flag, plus source URL.
One page at a time, a short delay, a clear user agent.
If a page is blocked, or shows a CAPTCHA, stop that retailer
and return no observation. Do not work around the block.
"""
