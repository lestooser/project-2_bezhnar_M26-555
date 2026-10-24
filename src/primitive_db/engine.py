import shlex

import prompt
from prettytable import PrettyTable

from .core import (
    DatabaseError,
    TableNotFoundError,
    create_table,
    delete,
    drop_table,
    insert,
    select,
    update,
)
from .parser import parse_condition, parse_values
from .utils import load_metadata, load_table_data, save_metadata, save_table_data

META_PATH = "db_meta.json"


def print_help() -> None:
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values (значение1, значение2) - добавить запись"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> - прочитать по условию"
    )
    print(
        "<command> update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение> - обновить"
    )
    print("<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить")
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run() -> None:
    print("\n ***База данных***")
    print(print_help())

    while True:
        user_input = prompt.string("Введите команду: ").strip()
        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Некорректное значение. Попробуйте снова")
            continue

        command, *rest = args
        if command in ("exit", "help"):
            match command:
                case "exit":
                    print("Выход из программы")
                    break
                case "help":
                    print_help()
            continue

        metadata = load_metadata(META_PATH)

        try:
            match command:
                case "create_table":
                    if len(rest) < 1:
                        print("Некорректное значение. Попробуйте снова")
                        continue
                    table_name, *columns = rest
                    metadata = create_table(metadata, table_name, columns)
                    save_metadata(META_PATH, metadata)
                    print(f"Таблица {table_name} создана")

                case "drop_table":
                    if len(rest) < 1:
                        print("Некорректное значение. Попробуйте снова")
                        continue

                    table_name = rest[0]
                    metadata = drop_table(metadata, table_name)
                    save_metadata(META_PATH, metadata)
                    print(f"Таблица {table_name} удалена")

                case "insert":
                    if len(rest) < 1:
                        print("Некорректное значение. Попробуйте снова")
                        continue
                    table_name = rest[1]

                    values_str = " ".join(rest[3:])
                    values = parse_values(values_str)

                    table_data = load_table_data(table_name)
                    table_data = insert(metadata, table_data, table_name, values)
                    save_table_data(table_name, table_data)
                    print(f"Запись успешно добавлена в таблицу {table_name}")

                case "select":
                    if len(rest) < 2 or rest[0] != "from":
                        print("Некорректное значение. Попробуйте снова")
                        continue

                    table_name = rest[1]
                    table_data = load_table_data(table_name)

                    where_clause = None

                    if len(rest) > 2 and rest[2] == "where":
                        where_str = " ".join(rest[3:])
                        where_clause = parse_condition(where_str)

                    result = select(table_data, where_clause)

                    if not isinstance(result, list) or not result:
                        print("Записей не найдено.")
                    else:
                        pt = PrettyTable()
                        pt.field_names = list(result[0].keys())
                        for row in result:
                            pt.add_row(list(row.values()))
                        print(pt)

                case "delete":
                    if len(rest) < 4 or rest[0] != "from" or rest[2] != "where":
                        print("Некорректное значение. Попробуйте снова")
                        continue
                    table_name = rest[1]
                    idx_where = rest.index("where")
                    where_str = " ".join(rest[idx_where:])

                    where_clause = parse_condition(where_str)

                    table_data = load_table_data(table_name)
                    table_data = delete(table_data, where_clause)
                    save_table_data(table_name, table_data)
                    print("Запись удалена")

                case "update":
                    if len(rest) < 5 or "set" not in rest or "where" not in rest:
                        print("Некорректное значение. Попробуйте снова")
                        continue
                    table_name = rest[1]
                    idx_set = rest.index("set")
                    idx_where = rest.index("where")

                    set_str = " ".join(rest[idx_set:idx_where])
                    where_str = " ".join(rest[idx_where:])

                    set_clause = parse_condition(set_str)
                    where_clause = parse_condition(where_str)

                    table_data = load_table_data(table_name)
                    table_data = update(table_data, set_clause, where_clause)

                    save_table_data(table_name, table_data)
                    print(f"Записи в таблице '{table_name}' успешно обновлены")

                case "info":
                    if len(rest) != 1:
                        print("Некорректное значение. Попробуйте снова")
                        continue
                    table_name = rest[0]
                    if table_name not in metadata:
                        raise TableNotFoundError(table_name)

                case "list_tables":
                    if not metadata:
                        print("Таблиц нет")
                    else:
                        for table_name in metadata:
                            print(f"- {table_name}")
                case _:
                    print(f"Функции {command} нет. Попробуйте снова")
        except DatabaseError as e:
            print(e)


if __name__ == "__main__":
    run()
