import sqlite3
from typing import Any, List, Tuple, Optional

def execute_query(*,db_path: str, query: str, params: Optional[Tuple[Any, ...]] = None) -> List[Tuple]:
    """
    Execute a SQL query on a SQLite database.

    Args:
        db_path (str): Path to the SQLite database file.
        query (str): SQL query string (can be parameterized or not).
        params (tuple, optional): Parameters for the query. Default is None.

    Returns:
        list[tuple]: Query result rows (if SELECT), otherwise an empty list.
    """
    results = []
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if query.strip().lower().startswith("select"):
                results = cursor.fetchall()
            else:
                conn.commit()
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    return results
