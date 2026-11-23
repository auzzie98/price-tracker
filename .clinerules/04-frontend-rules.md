# 04 Frontend rules

## Stack

- Plain HTML, CSS, and JavaScript. No framework, no build step, no Node.
- TradingView Lightweight Charts, Apache 2.0, loaded from CDN. Line and area series only in v1.
- One chart component in `web/static/js/chart.js`. Use it for every chart.

## One chart, two kinds of data

- Both views are the same line chart with the same time toggles. The only difference is the number on the vertical axis: dollars for a single product, or the index number for a group of products.
- Product page: sku_prices, dollar price, like a ticker.
- Category page: index_values, index number, like the S and P 500.
- Front page tiles: index_values, with current value, percent change, and a small chart.
- Time toggles are 1D, 1W, 1M, and 1Y, filtering the same series, not a different chart type.

## Pages

- `web/index.html`: index tiles on top, then the biggest movers list, with a 1D and 1W toggle. Leave room in the layout for the cheapest and most viewed lists later.
- `web/category.html`: full index chart for one category, plus the list of tracked products in it.
- `web/product.html`: dollar price chart for one exact product, plus which retailers its price comes from.
- `web/methodology.html`: how the index works, which sites are scraped, the v1 limits, and the cold start. Copy from METHODOLOGY.md, in plain words.

## Copy and style

- Strict black and white in v1, plain and readable. Charts use a single dark line on a white background, with a light grid.
- Headings are plain and literal. No clever claim style titles.
- On launch day the lists are empty, since movers need at least two data points per product. The site says so openly, in plain words.
- No tracking, no analytics, no ads, no affiliate links, no accounts in v1.
- Every price shows its source retailer. Every index page links to the methodology page.
