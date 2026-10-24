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


class TableData:
    def __init__(self, data: list[dict]) -> None:
        self.data = data

    def insert(self, metadata: dict, table_name: str, values: list) -> list[dict]:
        if table_name not in metadata:
            raise TableNotFoundError(table_name)

        columns = metadata[table_name]["columns"][1:]

        if len(values) != len(columns):
            raise InvalidValueError(values)

        for value, col in zip(values, columns):
            if col["type"] == "int" and (
                not isinstance(value, int) or isinstance(value, bool)
            ):
                raise InvalidValueError(value)
            elif col["type"] == "str" and not isinstance(value, str):
                raise InvalidValueError(value)
            elif col["type"] == "bool" and not isinstance(value, bool):
                raise InvalidValueError(value)

        new_id = max((row["ID"] for row in self.data), default=0) + 1

        new_row = {"ID": new_id}
        for value, col in zip(values, columns):
            new_row[col["name"]] = value

        self.data.append(new_row)
        return self.data

    def select(self, where_clause: dict | None = None) -> list[dict]:
        if where_clause is None:
            return self.data

        return [
            row
            for row in self.data
            if all(row.get(k) == v for k, v in where_clause.items())
        ]

    def update(self, set_clause: dict, where_clause: dict | None = None) -> list[dict]:
        for row in self.data:
            if all(row.get(k) == v for k, v in where_clause.items()):
                for key, new_v in set_clause.items():
                    if key in row:
                        row[key] = new_v
        return self.data

    def delete(self, where_clause: dict) -> list[dict]:
        self.data = [
            row
            for row in self.data
            if not all(row.get(k) == v for k, v in where_clause.items())
        ]
        return self.data


def load_metadata(filepath: str | Path) -> dict[str, Any]:
    return JsonStorage(filepath).load()


def save_metadata(filepath: str | Path, data: dict[str | Any]) -> None:
    JsonStorage(filepath).save(data)


def insert(
    metadata: dict, table_data: list[dict], table_name: str, values: list
) -> list[dict]:
    table = TableData(table_data)
    return table.insert(metadata, table_name, values)


def select(table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
    table = TableData(table_data)
    return table.select(where_clause)


def update(table_data: list[dict], set_clause: dict, where_clause: dict) -> list[dict]:
    table = TableData(table_data)
    return table.update(set_clause, where_clause)


def delete(table_data: list[dict], where_clause: dict) -> list[dict]:
    table = TableData(table_data)
    return table.delete(where_clause)


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
