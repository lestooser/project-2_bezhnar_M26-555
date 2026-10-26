from .constants import (
    COLUMN_SEPARATOR,
    ID_COLUMN_NAME,
    ID_COLUMN_TYPE,
    VALID_TYPES,
)
from .decorators import confirm_action, create_cacher, handle_db_errors, log_time

_select_cache = create_cacher()


def _invalidate_select_cache() -> None:
    """Сбрасывает кэш select — вызывать при любой мутации данных."""
    global _select_cache
    _select_cache = create_cacher()


class DatabaseError(Exception):
    """Базовая ошибка в БД"""


class TableAlreadyExistsError(DatabaseError):
    def __init__(self, name) -> None:
        """Создаёт ошибку для попытки повторно создать таблицу."""
        super().__init__(f"Таблица {name} уже существует")


class TableNotFoundError(DatabaseError):
    def __init__(self, name) -> None:
        """Создаёт ошибку для обращения к отсутствующей таблице."""
        super().__init__(f"Таблица {name} не существует")


class InvalidValueError(DatabaseError):
    def __init__(self, value) -> None:
        """Создаёт ошибку для значения, не прошедшего проверку."""
        self.value = value
        super().__init__(f"Некорректное значение: {value}")


class Column:
    """Описание колонки таблицы: имя и тип."""

    def __init__(self, name: str, type: str) -> None:
        """Проверяет и сохраняет имя и тип колонки."""
        if not name:
            raise InvalidValueError(name)

        if type not in VALID_TYPES:
            raise InvalidValueError(type)
        self.name = name
        self.type = type

    def to_dict(self) -> dict:
        """Возвращает описание колонки в виде словаря."""
        return {"name": self.name, "type": self.type}


class TableData:
    """Обёртка над списком строк таблицы с методами CRUD."""

    def __init__(self, data: list[dict]) -> None:
        """Сохраняет список строк таблицы для выполнения операций."""
        self.data = data

    def insert(self, metadata: dict, table_name: str, values: list) -> list[dict]:
        """Проверяет значения и добавляет новую строку с уникальным ID."""
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

        new_id = max((row[ID_COLUMN_NAME] for row in self.data), default=0) + 1

        new_row = {ID_COLUMN_NAME: new_id}
        for value, col in zip(values, columns):
            new_row[col["name"]] = value

        self.data.append(new_row)
        return self.data

    def select(self, where_clause: dict | None = None) -> list[dict]:
        """Возвращает все строки или строки, соответствующие условию."""
        if where_clause is None:
            return self.data

        return [
            row
            for row in self.data
            if all(row.get(k) == v for k, v in where_clause.items())
        ]

    def update(self, set_clause: dict, where_clause: dict | None = None) -> list[dict]:
        """Обновляет указанные поля строк, подходящих под условие."""
        for row in self.data:
            if all(row.get(k) == v for k, v in where_clause.items()):
                for key, new_v in set_clause.items():
                    if key in row:
                        row[key] = new_v
        return self.data

    def delete(self, where_clause: dict) -> list[dict]:
        """Удаляет строки, соответствующие условию, и возвращает оставшиеся."""
        self.data = [
            row
            for row in self.data
            if not all(row.get(k) == v for k, v in where_clause.items())
        ]
        return self.data


class Database:
    """Менеджер метаданных: создание и удаление таблиц."""

    def __init__(self, metadata: dict) -> None:
        """Сохраняет метаданные базы данных."""
        self.metadata = metadata

    def create_table(self, table_name: str, columns: list[str]):
        """Создаёт описание таблицы, проверив имена и типы её колонок."""
        if table_name in self.metadata:
            raise TableAlreadyExistsError(table_name)

        parsed = [Column(ID_COLUMN_NAME, ID_COLUMN_TYPE)]
        for raw in columns:
            if COLUMN_SEPARATOR not in raw:
                raise InvalidValueError(raw)
            name, type_col = raw.split(COLUMN_SEPARATOR, 1)
            parsed.append(Column(name, type_col))

        self.metadata[table_name] = {"columns": [c.to_dict() for c in parsed]}

    def drop_table(self, table_name: str):
        """Удаляет описание таблицы из метаданных."""
        if table_name not in self.metadata:
            raise TableNotFoundError(table_name)

        del self.metadata[table_name]


@handle_db_errors
def create_table(metadata, table_name, columns) -> dict:
    """Создаёт таблицу и возвращает обновлённые метаданные."""
    db = Database(metadata)
    db.create_table(table_name, columns)
    return db.metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name) -> dict:
    """Запрашивает подтверждение и возвращает метаданные без таблицы."""
    db = Database(metadata)
    db.drop_table(table_name)
    return db.metadata


@handle_db_errors
@log_time
def insert(
    metadata: dict, table_data: list[dict], table_name: str, values: list
) -> list[dict]:
    """Добавляет строку в таблицу и инвалидирует кэш выборки."""
    table = TableData(table_data)
    _invalidate_select_cache()
    return table.insert(metadata, table_name, values)


@handle_db_errors
@log_time
def select(table_data: list[dict], where_clause: dict | None = None) -> list[dict]:
    """Выбирает строки таблицы с использованием кэша результатов."""
    key = str(where_clause)
    return _select_cache(key, lambda: TableData(table_data).select(where_clause))


@handle_db_errors
def update(table_data: list[dict], set_clause: dict, where_clause: dict) -> list[dict]:
    """Обновляет строки таблицы и сбрасывает кэш выборки."""
    _invalidate_select_cache()
    table = TableData(table_data)
    return table.update(set_clause, where_clause)


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data: list[dict], where_clause: dict) -> list[dict]:
    """Удаляет подходящие строки после подтверждения и сбрасывает кэш."""
    table = TableData(table_data)
    _invalidate_select_cache()
    return table.delete(where_clause)
