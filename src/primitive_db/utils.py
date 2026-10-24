from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .core import InvalidValueError, TableNotFoundError


class JsonStorage:
    def __init__(self, filepath: str | Path):
        self.filepath = Path(filepath)

    def load(self) -> dict[str, Any]:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save(self, data: dict[str, Any]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)





def load_metadata(filepath: str | Path) -> dict[str, Any]:
    return JsonStorage(filepath).load()


def save_metadata(filepath: str | Path, data: dict[str | Any]) -> None:
    JsonStorage(filepath).save(data)


def load_table_data(table_name: str) -> list[dict]:
    filepath = Path(f"data/{table_name}.json")

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict]) -> None:
    Path("data").mkdir(exist_ok=True)
    filepath = Path(f"data/{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
