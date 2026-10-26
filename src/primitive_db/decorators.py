import functools

import prompt

from .constants import CONFIRM_YES


def handle_db_errors(func):
    """Перехватывает ошибки БД и печатает понятное сообщение."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Выполняет функцию и преобразует ошибки базы данных в сообщения."""
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
    """Фабрика декораторов: спрашивает y/n перед действием."""

    def decorator(func):
        """Оборачивает функцию запросом подтверждения перед выполнением."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            """Запрашивает подтверждение и запускает исходную функцию."""
            from .core import DatabaseError

            answer = (
                prompt.string(
                    f"Вы уверены, что хотите выполнить {action_name}? (y/n): "
                )
                .strip()
                .lower()
            )

            if answer != CONFIRM_YES:
                raise DatabaseError(f"Действие {action_name} отменено пользователем.")
            return func(*args, **kwargs)

        return wrapper

    return decorator


def log_time(func):
    """Замеряет время выполнения через time.monotonic()."""
    import time

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        """Измеряет длительность вызова и выводит её даже при ошибке."""
        start = time.monotonic()
        try:
            return func(*args, **kwargs)
        finally:
            elapsed = time.monotonic() - start
            print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")

    return wrapper


def create_cacher():
    """Возвращает кэширующую функцию с dict в замыкании."""
    cache = {}

    def cache_result(key, value_func):
        """Возвращает сохранённый результат либо вычисляет и кэширует его."""
        if key in cache:
            print(f"[cache] hit: {key}")
            return cache[key]
        print(f"[cache] miss: {key}")
        result = value_func()
        cache[key] = result
        return result

    return cache_result
