from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .constants import DATA_DIR, TABLE_DATA_TEMPLATE


class JsonStorage:
    def __init__(self, filepath: str | Path):
        """Инициализирует хранилище JSON по указанному пути."""
        self.filepath = Path(filepath)

    def load(self) -> dict[str, Any]:
        """Загружает JSON-словарь; при отсутствии файла возвращает пустой."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except FileNotFoundError:
            return {}
        return data if isinstance(data, dict) else {}

    def save(self, data: dict[str, Any]) -> None:
        """Сохраняет словарь в JSON-файл в читаемом формате UTF-8."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def load_metadata(filepath: str | Path) -> dict[str, Any]:
    """Загружает метаданные базы данных из JSON-файла."""
    return JsonStorage(filepath).load()


def save_metadata(filepath: str | Path, data: dict[str | Any]) -> None:
    """Сохраняет метаданные базы данных в JSON-файл."""
    JsonStorage(filepath).save(data)


def load_table_data(table_name: str) -> list[dict]:
    """Загружает строки таблицы; если её файла нет, возвращает пустой список."""
    filepath = Path(TABLE_DATA_TEMPLATE.format(table_name=table_name))

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохраняет строки таблицы в JSON-файл, предварительно создавая каталог."""
    Path(DATA_DIR).mkdir(exist_ok=True)
    filepath = Path(TABLE_DATA_TEMPLATE.format(table_name=table_name))

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
