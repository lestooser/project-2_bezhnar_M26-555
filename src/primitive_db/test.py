from primitive_db.core import create_table, drop_table, TableNotFoundError

# 1. Создали и удалили
meta = create_table({}, "users", ["name:str"])
print(meta)
meta = drop_table(meta, "users")
print(meta)
# {}


# 2. Удаляем несуществующую
try:
    drop_table({}, "products")
except TableNotFoundError as e:
    print(e)
# Ошибка: Таблица "products" не существует.


# 3. Одна из двух таблиц — вторая остаётся
meta = create_table({}, "users", ["name:str"])
meta = create_table(meta, "products", ["title:str"])
meta = create_table(meta, "sdfsdfs", ["title:str"])
meta = drop_table(meta, "users")
print(list(meta.keys()))
# ['products']


# 4. Связка с utils
from primitive_db.utils import save_metadata, load_metadata
save_metadata("db_meta.json", meta)
print(load_metadata("db_meta.json"))   # True
print(meta)


from primitive_db.parser import parse_values, parse_condition

# Проверка значений
print(parse_values('("Sergei", 28, true)'))  # Ожидаем: ['Sergei', 28, True]
print(parse_values('(1, "Anna", false)'))    # Ожидаем: [1, 'Anna', False]

# Проверка условий
print(parse_condition("age = 28"))           # Ожидаем: {'age': 28}
print(parse_condition("name = 'Sergei'"))    # Ожидаем: {'name': 'Sergei'}
print(parse_condition("is_active = true"))   # Ожидаем: {'is_active': True}
