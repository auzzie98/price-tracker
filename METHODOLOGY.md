# Methodology

This file is the method. Code must match it. If code and this file disagree, this file wins until DECISIONS.md records a change.

## What the index is

The index tracks percent price change across a basket of SKUs, starting at 100. It is not an average dollar price.

Why not a plain average: when a 900 dollar premium model launches next to 550, 600, and 650 dollar cards, the average dollar price jumps 12.5 percent even though no price changed. The index leaves a new SKU out until it has its own history.

## Method, in steps

v1 uses a chained, equal weighted, matched model index.

1. Day 1 index is 100.
2. For each SKU listed on both days, price relative is today median price divided by yesterday median price.
3. Average the price relatives across those SKUs.
4. Today index is yesterday index times that average.

In math notation, with stacked fractions:

$$
I_t = I_{t-1} \times \frac{1}{n} \sum_{i=1}^{n} \frac{p_{i,t}}{p_{i,t-1}}
$$

Where:
- $I_t$ is the index on day $t$
- $I_{t-1}$ is the index on the previous period
- $n$ is the number of SKUs used on day $t$
- $p_{i,t}$ is the median price of SKU $i$ on day $t$
- $p_{i,t-1}$ is the median price of SKU $i$ on the previous period

A SKU price is the median across in stock retailers per period. The index averages each SKU own percent change, never dollar prices across different products.

## Launch baseline and eligible observations

`index_baseline_period` in `config/settings.yaml` sets Day 1. The current launch baseline is 2026-11-23, and earlier periods do not enter the published index. Observations from `example.com/mock` are not eligible for derived prices. An invalid observation can be kept in the append-only source table and excluded from derived data with a recorded reason in `observation_exclusions`.

## Worked example

Median price per SKU per day, in dollars:

| SKU | Day 1 | Day 2 | Day 3 | Day 4 |
| --- | --- | --- | --- | --- |
| A | 500 | 490 | 490 | 480.20 |
| B | 600 | 600 | 570 | 570 |
| C | 700 | 693 | 693 | 693 |
| D | none | none | 900 | 855 |

| Day | Average price relative | SKUs used | Index |
| --- | --- | --- | --- |
| 1 | start | 3 | 100.00 |
| 2 | 0.9900 | 3 | 99.00 |
| 3 | 0.9833 | 3 | 97.35 |
| 4 | 0.9825 | 4 | 95.65 |

Check Day 2: relatives are 490 divided by 500, 600 divided by 600, and 693 divided by 700. That is 0.98, 1.00, and 0.99. The average is 0.99. Index is 100 times 0.99, which is 99.00.
Check Day 3: relatives are 490 divided by 490, 570 divided by 600, and 693 divided by 693. That is 1.00, 0.95, and 1.00. The average is 0.9833. Index is 99.00 times 0.9833, which is 97.35.
Check Day 4: relatives are 480.20 divided by 490, 570 divided by 570, 693 divided by 693, and 855 divided by 900. That is 0.98, 1.00, 1.00, and 0.95. The average is 0.9825. Index is 97.35 times 0.9825, which is 95.65.

On Day 3, D is new and has nothing to compare against, so it is skipped. On Day 4 it counts, through its own change only. An index of 95.65 means the basket is about 4.35 percent cheaper than on Day 1.

This worked example is also a test. See `tests/test_index.py`. The test must use these exact numbers.

## Data layers

| Table | Holds | Rebuildable |
| --- | --- | --- |
| observations | timestamp, SKU, retailer, price, in stock flag | No, this is the source of truth |
| observation_exclusions | raw observation ID and reason it is left out of derived prices | No, audit record |
| sku_prices | SKU, period, median price | Yes |
| index_values | category, period, index value, SKUs used | Yes |

Because steps 2 and 3 can be rebuilt from step 1, the refresh interval and the formula can change later without losing data.

## index_values, kept and grown

index_values is kept and grows each period. Each new period, the job adds one new row per category and leaves the old rows alone, so the chart reads a stored history.

It is not wiped as a routine step. It can be rebuilt, because it is calculated from sku_prices, which is calculated from observations.

Rebuild only in these cases:
- The formula changes, such as adding weighting. Old rows would be inconsistent with the new method, so recompute them from the raw data.
- A scraping or matching bug produced bad prices. Fix it, then recompute the affected dates.
- The refresh interval or period length changes.

Rebuilding is only possible because we keep the raw observations. Without them, a bad index row would be permanent. With them, any derived table can be regenerated.

Revision rule: if a rebuild ever changes published numbers, the site must say so, since economists will care about revisions. That is how official statistics handle it too. Record the change, the dates affected, and the reason, on the methodology page.

### Published index revision, 2026-11-24

The initial Home page values were not valid market movements. The index history started before the launch baseline and included mock observations. The GPU value of 81.03 on Nov 24 had zero matched SKUs and no valid catalog observations. The CPU values of 89.23 on Nov 23 and 105.96 on Nov 24 included mock history, the old approved $220.00 Ryzen 5 9600X receipt, and a stale Ryzen 7 9800X3D derived row without a matching raw observation. The RAM value of 268.02 on Nov 23 came from mock history for the Corsair Vengeance 32GB DDR5-6000 CL30 kit; there was no Nov 24 RAM observation.

The derived tables were rebuilt with Nov 23 as Day 1. The corrected Nov 23 values are 100.00 for GPUs, CPUs, and RAM, using 9, 10, and 7 SKUs. There are no valid post-baseline observations yet, so no later category change is published. The 87 mock observations and the old receipt remain in the raw observation table, but they no longer affect derived prices.

## Known v1 limits, stated openly on the site

- Equal weighting: a 150 dollar RAM kit moves the index as much as a 2,000 dollar GPU.
- No quality adjustment: a faster card at the same price does not register as a price drop.
- No rule yet for a SKU that goes out of stock for days. That rule is decided during prototyping, see TASKS.md.
- Cold start: charts begin at launch and history accumulates. No backfill in v1.
- Refresh interval is decided during prototyping. Provisional default is 6 hours, in `config/settings.yaml`.

## Charts

One chart, two kinds of data. Both views are the same line chart with the same time toggles. The only difference is the number on the vertical axis: dollars for a single product, or the index number for a group of products.

- Product page: sku_prices, dollar price, like a ticker.
- Category page: index_values, index number, like the S and P 500.
- Front page tiles: index_values, with current value, percent change, and a small chart.

index_values is the list of dots on the line for a category chart. One row is one dot, and the chart connects them.

The reason an index exists at all is that the price of all GPUs is not one real dollar figure. A 300 dollar card and a 2,000 dollar card cannot be averaged into a meaningful price, so we track how much prices moved instead. That moved by number is the index, and index_values stores it day by day so the chart does not have to recalculate everything every time someone loads a page.
