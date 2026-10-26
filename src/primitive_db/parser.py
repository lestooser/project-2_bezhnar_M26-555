def parse_values(values_str: str) -> list:
    """Разбирает строку значений, преобразуя кавычки, числа и булевы значения."""
    values_str = values_str.strip()
    if values_str.startswith("(") and values_str.endswith(")"):
        values_str = values_str[1:-1]

    if not values_str:
        return []

    raw_values = [v.strip() for v in values_str.split(",")]
    result = []

    for v in raw_values:
        if (v.startswith('"') and v.endswith('"')) or (
            v.startswith("'") and v.endswith("'")
        ):
            result.append(v[1:-1])

        elif v.lower() == "true":
            result.append(True)
        elif v.lower() == "false":
            result.append(False)
        else:
            try:
                result.append(int(v))
            except ValueError:
                result.append(v)
    return result


def parse_condition(clause: str) -> dict:
    """Разбирает условие вида «столбец = значение» в словарь."""
    if "=" not in clause:
        raise ValueError(f"Некорректное условие: {clause}")

    col_name, raw_value = clause.split("=", 1)
    col_name = col_name.strip()
    raw_value = raw_value.strip()

    if (raw_value.startswith('"') and raw_value.endswith('"')) or (
        raw_value.startswith("'") and raw_value.endswith("'")
    ):
        return {col_name: raw_value[1:-1]}

    if raw_value.lower() == "true":
        return {col_name: True}
    if raw_value.lower() == "false":
        return {col_name: False}

    try:
        return {col_name: int(raw_value)}
    except ValueError:
        return {col_name: raw_value}
