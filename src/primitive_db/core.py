class DatabaseError(Exception):
    """Базовая ошибка в БД"""


class TableAlreadyExistsError(DatabaseError):
    def __init__(self, name) -> None:
        super().__init__(f"Таблица {name} уже существует")


class TableNotFoundError(DatabaseError):
    def __init__(self, name) -> None:
        super().__init__(f"Таблица {name} не существует")


class InvalidValueError(DatabaseError):
    def __init__(self, value) -> None:
        self.value = value
        super().__init__(f"Некорректное значение: {value}")


class Column:
    def __init__(self, name: str, type: str) -> None:
        if not name:
            raise InvalidValueError(name)

        if type not in ("int", "str", "bool"):
            raise InvalidValueError(type)
        self.name = name
        self.type = type

    def to_dict(self) -> dict:
        return {"name": self.name, "type": self.type}


class Table:
    def __init__(self, name: str, columns: list[Column]) -> None:
        self.name = name
        self.columns = [Column("ID", "int")] + columns


class Database:
    def __init__(self, metadata: dict) -> None:
        self.metadata = metadata

    def load(self):
        self.tables = self.storage.load()

    def save(self):
        self.storage.save(self.tables)

    def create_table(self, table_name: str, columns: list[str]):
        if table_name in self.metadata:
            raise TableAlreadyExistsError

        parsed = [Column("ID", "int")]
        for raw in columns:
            if ":" not in raw:
                raise InvalidValueError
            name, type_col = raw.split(":", 1)
            parsed.append(Column(name, type_col))

        self.metadata[table_name] = {"columns": [c.to_dict() for c in parsed]}

    def drop_table(self, table_name: str):
        if table_name not in self.metadata:
            raise TableNotFoundError(table_name)

        del self.metadata[table_name]


def create_table(metadata, table_name, columns) -> dict:
    db = Database(metadata)
    db.create_table(table_name, columns)
    return db.metadata


def drop_table(metadata, table_name) -> dict:
    db = Database(metadata)
    db.drop_table(table_name)
    return db.metadata
