# Lógica CRUD genérica
from .db import get_connection

def crud_action(action: str, table: str, data: dict = None, where: dict = None):
    conn = get_connection()
    if not conn:
        return {"connected": False}

    with conn.cursor() as cur:
        if action == "create":
            keys = ", ".join(data.keys())
            values = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO {table} ({keys}) VALUES ({values})"
            cur.execute(sql, tuple(data.values()))

        elif action == "read":
            sql = f"SELECT * FROM {table}"
            cur.execute(sql)
            return cur.fetchall()

        elif action == "update":
            sets = ", ".join([f"{k}=%s" for k in data.keys()])
            wheres = " AND ".join([f"{k}=%s" for k in where.keys()])
            sql = f"UPDATE {table} SET {sets} WHERE {wheres}"
            cur.execute(sql, (*data.values(), *where.values()))

        elif action == "delete":
            wheres = " AND ".join([f"{k}=%s" for k in where.keys()])
            sql = f"DELETE FROM {table} WHERE {wheres}"
            cur.execute(sql, tuple(where.values()))

        conn.commit()

    return {"connected": True, "action": action}
