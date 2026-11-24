"""Diagnostic script to find the exit code 1 cause"""
import sys
from pathlib import Path

# Simulate what serve.py does
script_path = Path(__file__).resolve()
print(f"Script path: {script_path}")

parents1 = script_path.parents[1]
print(f"Parents[1]: {parents1}")

src_path = parents1 / "src"
print(f"Src path: {src_path}")

# Check if src exists
print(f"Src exists: {src_path.exists()}")

# Check if src/price_tracker exists
pt_path = src_path / "price_tracker"
print(f"price_tracker exists: {pt_path.exists()}")

# Check if src/price_tracker/db.py exists
db_module = src_path / "price_tracker" / "db.py"
print(f"db.py exists: {db_module.exists()}")

# Check the data directory
data_path = parents1 / "data"
print(f"Data dir exists: {data_path.exists()}")

# Check if data/price-tracker.db exists
db_file = data_path / "price-tracker.db"
print(f"DB file exists: {db_file.exists()}")

# Check schema.sql
schema_path = parents1 / "db" / "schema.sql"
print(f"Schema exists: {schema_path.exists()}")

# Test the import
sys.path.insert(0, str(src_path))
try:
    from price_tracker.db import init_database
    print("Import success: price_tracker.db imported OK")
except ImportError as e:
    print(f"Import FAILED: {e}")
except Exception as e:
    print(f"Import error: {type(e).__name__}: {e}")

# Test relative vs absolute path
print(f"\nRelative path 'data/price-tracker.db': {'data/price-tracker.db'}")
print(f"Absolute path via Path(__file__): {parents1 / 'data' / 'price-tracker.db'}")
print(f"Absolute path exists: {(parents1 / 'data' / 'price-tracker.db').exists()}")