-- Price Tracker schema, SQLite.
-- Source of truth. scripts/init_db.py creates the database from this file.
-- It must be safe to run twice. It must not delete existing observations.

CREATE TABLE IF NOT EXISTS retailers (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  base_url TEXT NOT NULL,
  enabled INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS skus (
  id TEXT PRIMARY KEY,
  mpn TEXT NOT NULL,
  brand TEXT NOT NULL,
  model TEXT NOT NULL,
  category TEXT NOT NULL,
  chip TEXT,
  architecture TEXT
);

CREATE TABLE IF NOT EXISTS sku_retailer_urls (
  sku_id TEXT NOT NULL,
  retailer_id TEXT NOT NULL,
  url TEXT NOT NULL,
  active INTEGER NOT NULL DEFAULT 1,
  PRIMARY KEY (sku_id, retailer_id),
  FOREIGN KEY (sku_id) REFERENCES skus(id),
  FOREIGN KEY (retailer_id) REFERENCES retailers(id)
);

CREATE TABLE IF NOT EXISTS observations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  observed_at TEXT NOT NULL,
  sku_id TEXT NOT NULL,
  retailer_id TEXT NOT NULL,
  price_cents INTEGER NOT NULL,
  in_stock INTEGER NOT NULL,
  source_url TEXT NOT NULL,
  FOREIGN KEY (sku_id) REFERENCES skus(id),
  FOREIGN KEY (retailer_id) REFERENCES retailers(id)
);

CREATE TABLE IF NOT EXISTS sku_prices (
  sku_id TEXT NOT NULL,
  period TEXT NOT NULL,
  median_price_cents INTEGER NOT NULL,
  retailers_used INTEGER NOT NULL,
  PRIMARY KEY (sku_id, period),
  FOREIGN KEY (sku_id) REFERENCES skus(id)
);

CREATE TABLE IF NOT EXISTS index_values (
  category TEXT NOT NULL,
  period TEXT NOT NULL,
  index_value REAL NOT NULL,
  skus_used INTEGER NOT NULL,
  PRIMARY KEY (category, period)
);

CREATE TABLE IF NOT EXISTS page_views (
  sku_id TEXT NOT NULL,
  viewed_on TEXT NOT NULL,
  views INTEGER NOT NULL DEFAULT 0,
  PRIMARY KEY (sku_id, viewed_on),
  FOREIGN KEY (sku_id) REFERENCES skus(id)
);

CREATE INDEX IF NOT EXISTS idx_observations_sku_time
  ON observations(sku_id, observed_at);
CREATE INDEX IF NOT EXISTS idx_sku_prices_sku_period
  ON sku_prices(sku_id, period);
CREATE INDEX IF NOT EXISTS idx_index_values_category_period
  ON index_values(category, period);
