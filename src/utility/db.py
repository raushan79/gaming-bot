import psycopg2
from psycopg2 import extras
import threading

class PostgresDB:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(PostgresDB, cls).__new__(cls)
                    cls._instance._init_connection(*args, **kwargs)
                    cls._instance._connection_args = kwargs
                    cls._instance._connection_url = kwargs.get("url", None)
        return cls._instance

    def _init_connection(self, url=None, **kwargs):
        try:
            if url:
                self.conn = psycopg2.connect(dsn=url)
            else:
                self.conn = psycopg2.connect(**kwargs)
            self.conn.autocommit = True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to database: {e}")

    def _ensure_connection(self):
        """
        Ensure connection is alive. If not, reconnect using stored params.
        """
        if not hasattr(self, "conn") or self.conn.closed:
            print("Re-establishing lost database connection...")
            if hasattr(self, "_connection_url") and self._connection_url:
                self._init_connection(url=self._connection_url)
            elif hasattr(self, "_connection_args"):
                self._init_connection(**self._connection_args)
            else:
                raise ConnectionError("No connection info available to reconnect.")

    def execute(self, query, params=None, fetch=False):
        self._ensure_connection()

        try:
            with self.conn.cursor(cursor_factory=extras.RealDictCursor) as cur:
                cur.execute(query, params)
                if fetch:
                    return cur.fetchall()
        except Exception as e:
            print(f"Query execution error: {e}")
            return None

    def close(self):
        # Prevent closing the singleton connection
        raise RuntimeError("This singleton database connection cannot be closed manually.")
