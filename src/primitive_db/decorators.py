import functools

import prompt


def handle_db_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. Возможно, база данных "
                "не инициализирована."
            )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            # Добавляем распознавание наших кастомных ошибок
            from .core import DatabaseError

            if isinstance(e, DatabaseError):
                print(e)
            else:
                print(f"Произошла непредвиденная ошибка: {e}")

    return wrapper


def confirm_action(action_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            from .core import DatabaseError

            answer = (
                prompt.string(
                    f"Вы уверены, что хотите выполнить {action_name}? (y/n): "
                )
                .strip()
                .lower()
            )

            if answer != "y":
                raise DatabaseError(f"Действие {action_name} отменено пользователем.")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")

    return wrapper


def create_cacher():
    cache = {}

    def cache_result(key, value_func):
        if key in cache:
            print(f"[cache] hit: {key}")
            return cache[key]
        print(f"[cache] miss: {key}")
        result = value_func()
        cache[key] = result
        return result

    return cache_result
