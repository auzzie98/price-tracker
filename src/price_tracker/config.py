"""Load configuration files for Price Tracker.

Config files: config/settings.yaml, config/retailers.yaml,
config/products.yaml. Code reads config, it does not hard code
retailer URLs, product lists, or refresh intervals.
"""

from __future__ import annotations

from pathlib import Path

import yaml


def repo_root() -> Path:
    """Return the repository root folder."""
    return Path(__file__).resolve().parents[2]


def config_dir() -> Path:
    """Return the config folder."""
    return repo_root() / "config"


def load_settings() -> dict:
    """Load config/settings.yaml."""
    path = config_dir() / "settings.yaml"
    with path.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_retailers() -> list[dict]:
    """Load the retailer list from config/retailers.yaml."""
    path = config_dir() / "retailers.yaml"
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data.get("retailers", [])


def load_products() -> list[dict]:
    """Load the product list from config/products.yaml."""
    path = config_dir() / "products.yaml"
    with path.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data.get("products", [])
