# Start prototype

Use this workflow when Austin says to start the prototype, or when Task 1 in TASKS.md is the current task.

## Steps

1. Read TASKS.md Task 1, AGENTS.md, and .clinerules/00-read-first.md.
2. Create the folder structure in ARCHITECTURE.md, if any folder is missing.
3. Create `requirements.txt` with only the packages listed in PROJECT_PLAN.md, with pinned versions you verify at install time.
4. Create the empty library files in `src/price_tracker/` and the thin scripts in `scripts/`, with no fake implementation.
5. Run the Task 1 check from TASKS.md, and report the exact output.

## Run commands, Windows, from the repo root

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Done check

Task 1 in TASKS.md is green, and no script claims to work before its check passes.
