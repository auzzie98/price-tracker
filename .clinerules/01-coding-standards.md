# 01 Coding standards

## Python

- Python 3.12, Windows, virtual environment, `python`, activate with `venv\Scripts\activate`.
- Plain, readable code. One function does one job. Typed where it helps, no clever one liners.
- Library code lives in `src/price_tracker/`. Scripts live in `scripts/` and are thin, they parse arguments and call library code.
- No script in `src/` reads the command line or writes files on import.
- Tests use the Python standard library only, run with `python -m unittest discover -s tests -v`.
- Do not add a dependency without a reason written in DECISIONS.md and in the task note. Update `requirements.txt` in the same task.

## Frontend

- Plain HTML, CSS, and JavaScript. No framework, no build step, no Node.
- One chart component in `web/static/js/chart.js`, using TradingView Lightweight Charts, line and area series only in v1.
- The same component draws dollar charts and index charts. The only difference is the vertical axis label and the data source.
- Strict black and white in v1, plain and readable. Charts use a single dark line on a white background, with a light grid.
- No tracking, no analytics, no ads, no affiliate links.

## Files and naming

- Use the folder structure in ARCHITECTURE.md. Do not invent a new top level folder without a decision.
- Config holds settings, retailers, and products. Code reads config, it does not hard code retailer URLs, product lists, or refresh intervals.
- Keep file names lower case, with hyphens for docs and underscores for Python modules.

## Checks

- Run the check listed in TASKS.md for the task you are on, before moving to the next task.
- A check that fails is the work. Fix it, do not skip it and do not mark the task done.
