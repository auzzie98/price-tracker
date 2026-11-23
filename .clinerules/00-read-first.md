# 00 Read first

You are Cline, the coding agent for Price Tracker. Work from TASKS.md, one task at a time, in order. Do not skip ahead.

## Before any code change

1. Read TASKS.md, find the current task, and read its goal and its done check.
2. Read AGENTS.md.
3. Read the files listed for that task type below.
4. Do the smallest step that makes the check green, then run the check. If it fails, fix it before moving on.

## Files to read first, by task

- Any task: TASKS.md, AGENTS.md, PROJECT_PLAN.md
- Index math: METHODOLOGY.md, tests/test_index.py, .clinerules/03-data-and-index-rules.md
- Database: db/schema.sql, .clinerules/03-data-and-index-rules.md
- Scraper or retailer: RETAILER_FEASIBILITY.md, config/retailers.yaml, config/products.yaml, .clinerules/02-scraping-rules.md
- Frontend or chart: ARCHITECTURE.md, .clinerules/04-frontend-rules.md
- Plan or scope change: PROJECT_PLAN.md, DECISIONS.md. Do not change scope in a code file alone.

## Context tips, free model

- The model is Nemotron 3.5 Super VL first, hosted context listed at 262K, weights up to 1M tokens. Plan work for 262K. Keep each task small, one file or one small change per edit.
- If the task needs a file, read that file first, do not guess its contents.
- If you describe a command in prose instead of running it, stop, switch to Nemotron 3 Super, and try the same small task again.
- If you hit a 429 rate limit, stop, wait, and tell Austin. Do not retry in a loop.
- Keep API keys and private data out of prompts, files, and scraped output.

## Hard stops

- Never edit data/ by hand. Observations are append only.
- Never invent a price, a retailer result, a license, or a hosting fact. Mark it as to check.
- Never add accounts, tracking, ads, affiliate links, or analytics in v1.
- Never use em dashes or arrow characters in docs, code comments, or user facing copy.
- Never commit a database file, an API key, or a private file.
- Final report, always: end every task with one final report inside a single code block, so Austin can copy it. Do not end with plain chat text only, and do not end with no report. The code block must include: task name and status, files changed, exact command output for tests, URLs checked with status 200 or 404, and what is next. Do not start the next task in the same report. Stop after the code block and wait for Austin.
