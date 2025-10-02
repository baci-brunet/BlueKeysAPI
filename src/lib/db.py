import os, traceback
import pymysql
from typing import Optional, Any, Dict, List, Tuple

_connection: Optional[pymysql.connections.Connection] = None


def get_connection() -> pymysql.connections.Connection:
    """
    Get (and cache) a pymysql connection to RDS.
    Connection is reused across warm Lambda invocations.
    """
    global _connection
    if _connection and _connection.open:
        return _connection

    _connection = pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    return _connection

def fetch_all(query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    except pymysql.MySQLError as e:
        # Log and raise — you can swap print for structured logging
        print(f"[DB ERROR] fetch_all failed: {e}")
        raise
    except Exception as e:
        print(f"[UNEXPECTED ERROR] fetch_all failed: {e}")
        raise

def execute(sql: str, params=None):
    """
    Run INSERT/UPDATE/DELETE. Returns dict(rowcount, lastrowid).
    """
    conn = None
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            if params is None:
                cur.execute(sql)
            else:
                if not isinstance(params, (tuple, list, dict)):
                    params = (params,)
                cur.execute(sql, params)
            return {"rowcount": cur.rowcount, "lastrowid": cur.lastrowid}
    except Exception as e:
        print("[DB EXEC ERROR]", repr(e))
        print(traceback.format_exc())
        raise
    finally:
        try:
            if conn: conn.close()
        except Exception:
            pass