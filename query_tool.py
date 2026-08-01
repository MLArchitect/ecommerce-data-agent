import sys
import json
from db import run_query, get_schema_info


def do_schema():
    columns, rows = get_schema_info()
    tables = {}
    for row in rows:
        schema, table, col, dtype, nullable = row
        key = f"{schema}.{table}"
        if key not in tables:
            tables[key] = []
        tables[key].append({"column": col, "type": dtype, "nullable": nullable})

    for table_name, cols in tables.items():
        print(f"\n=== {table_name} ===")
        for c in cols:
            null_str = "NULL" if c["nullable"] == "YES" else "NOT NULL"
            print(f"  {c['column']:30s} {c['type']:15s} {null_str}")


def do_query(sql):
    sql = sql.strip()
    if not sql.upper().startswith("SELECT"):
        print("ERROR: Only SELECT queries are allowed.")
        sys.exit(1)
    columns, rows = run_query(sql)
    widths = [len(c) for c in columns]
    for row in rows:
        for i, val in enumerate(row):
            widths[i] = max(widths[i], len(str(val)))
    header = " | ".join(c.ljust(widths[i]) for i, c in enumerate(columns))
    separator = "-+-".join("-" * w for w in widths)
    print(header)
    print(separator)
    for row in rows:
        print(" | ".join(str(val).ljust(widths[i]) for i, val in enumerate(row)))
    print(f"\n({len(rows)} row(s) returned)")


def do_sample(table_name):
    sql = f"SELECT TOP 5 * FROM {table_name}"
    do_query(sql)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python query_tool.py schema")
        print("  python query_tool.py query \"SELECT ...\"")
        print("  python query_tool.py sample <table_name>")
        sys.exit(1)

    command = sys.argv[1]
    if command == "schema":
        do_schema()
    elif command == "query" and len(sys.argv) >= 3:
        do_query(sys.argv[2])
    elif command == "sample" and len(sys.argv) >= 3:
        do_sample(sys.argv[2])
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
