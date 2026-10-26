"""Константы проекта Primitive DB."""

# ── Файловая система ──────────────────────────────────────────
META_FILE = "db_meta.json"
DATA_DIR = "data"
TABLE_DATA_TEMPLATE = "data/{table_name}.json"

# ── Схема таблицы ─────────────────────────────────────────────
ID_COLUMN_NAME = "ID"
ID_COLUMN_TYPE = "int"
VALID_TYPES = frozenset({"int", "str", "bool"})
COLUMN_SEPARATOR = ":"

# ── Подтверждение операций ────────────────────────────────────
CONFIRM_YES = "y"

# ── Команды REPL ──────────────────────────────────────────────
CMD_EXIT = "exit"
CMD_HELP = "help"
CMD_CREATE_TABLE = "create_table"
CMD_DROP_TABLE = "drop_table"
CMD_INSERT = "insert"
CMD_SELECT = "select"
CMD_UPDATE = "update"
CMD_DELETE = "delete"
CMD_INFO = "info"
CMD_LIST_TABLES = "list_tables"

# ── Ключевые слова внутри команд ──────────────────────────────
KW_FROM = "from"
KW_WHERE = "where"
KW_SET = "set"
KW_TRUE = "true"
KW_FALSE = "false"
EQUAL_SIGN = "="
PAIR_SEPARATOR = ","
QUOTE_CHARS = ("'", '"')
