import duckdb
import os

def find_by_field_and_location(db_path, field, location):
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"DB not found at: {db_path}")
    conn = duckdb.connect(database=db_path, read_only=True)
    field = field.strip().rstrip('s')
    location = location.strip()
    query = "SELECT * FROM users WHERE Location ILIKE ? AND Occupation ILIKE ?"
    result = conn.execute(query, (f"%{location}%", f"%{field}%")).fetchall()
    conn.close()

    print(f"[DEBUG] Found {len(result)} rows")
    return result

def run_duckdb_query(query, db_path="data/users.db"):
    try:
        conn = duckdb.connect(db_path)
        result = conn.execute(query).fetchall()
        conn.close()

        if not result:
            return "No results."
        return "\n".join(str(row) for row in result)
    except Exception as e:
        return f"[DuckDB Error] {str(e)}"
