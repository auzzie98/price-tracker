# Run checks

Use this workflow before marking any task done, and before any package step.

## Run commands, Windows, from the repo root, with the virtual environment active

```
venv\Scripts\activate
python -m unittest discover -s tests -v
python scripts\init_db.py
python scripts\build_derived.py
python scripts\serve.py
```

## What to check

1. Tests pass, including `tests/test_index.py` with the worked example, 100.00, 99.00, 97.35, and 95.65.
2. `init_db.py` is safe to run twice, and does not delete existing observations.
3. `build_derived.py` is safe to rerun, and does not duplicate rows.
4. `serve.py` starts, and `GET /api/health` returns row counts for observations, sku_prices, and index_values.
5. No file in the repo contains an API key, a password, or a private file. Check `.gitignore` covers `data/`.

## If a check fails

Fix it before moving on. Do not mark the task done, and do not start the next task. Report the exact command and the exact error to Austin.
