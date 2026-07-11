import sqlite3


class Database:

    def __init__(
        self,
        db_name="items.db",
        busy_timeout_ms=5000,
        enable_wal=True,
    ):

        self.conn = sqlite3.connect(db_name)

        self.cursor = self.conn.cursor()

        self._configure_connection(
            busy_timeout_ms=busy_timeout_ms,
            enable_wal=enable_wal,
        )

        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS items(
                id TEXT PRIMARY KEY,
                keyword TEXT,
                title TEXT,
                price INTEGER,
                url TEXT,
                status TEXT,
                ignore_reason TEXT,
                first_seen TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        self._ensure_column("keyword", "TEXT")
        self._ensure_column("title", "TEXT")
        self._ensure_column("price", "INTEGER")
        self._ensure_column("url", "TEXT")
        self._ensure_column("status", "TEXT")
        self._ensure_column("ignore_reason", "TEXT")
        self._ensure_column("first_seen", "TEXT")

        self._create_indexes()

        self.conn.commit()

    def _configure_connection(
        self,
        busy_timeout_ms,
        enable_wal,
    ):

        self.cursor.execute(
            f"PRAGMA busy_timeout = {int(busy_timeout_ms)}"
        )

        if enable_wal:
            self.cursor.execute("PRAGMA journal_mode=WAL")
            self.cursor.execute("PRAGMA synchronous=NORMAL")

    def _ensure_column(self, column_name, column_type):

        self.cursor.execute("PRAGMA table_info(items)")

        columns = [
            row[1]
            for row in self.cursor.fetchall()
        ]

        if column_name in columns:
            return

        self.cursor.execute(
            f"ALTER TABLE items ADD COLUMN "
            f"{column_name} {column_type}"
        )

    def _create_indexes(self):

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_items_keyword
            ON items(keyword)
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_items_status
            ON items(status)
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_items_first_seen
            ON items(first_seen)
            """
        )

    def exists(self, item_id):

        self.cursor.execute(
            "SELECT 1 FROM items WHERE id=?",
            (item_id,)
        )

        return self.cursor.fetchone() is not None

    def get_existing_ids(self, item_ids):
        if not item_ids:
            return set()

        placeholders = ", ".join(
            "?"
            for _ in item_ids
        )

        self.cursor.execute(
            f"""
            SELECT id
            FROM items
            WHERE id IN ({placeholders})
            """,
            tuple(item_ids),
        )

        return {
            row[0]
            for row in self.cursor.fetchall()
        }

    def count_items(self):

        self.cursor.execute("SELECT COUNT(*) FROM items")

        return self.cursor.fetchone()[0]

    def count_items_by_status(self):

        counts = {
            "total": self.count_items(),
            "notified": 0,
            "ignored": 0,
            "baseline": 0,
        }

        self.cursor.execute(
            """
            SELECT status, COUNT(*)
            FROM items
            GROUP BY status
            """
        )

        for status, count in self.cursor.fetchall():
            if status in counts:
                counts[status] = count

        return counts

    def count_items_by_keyword(self):

        counts = {}

        self.cursor.execute(
            """
            SELECT
                keyword,
                status,
                COUNT(*)
            FROM items
            GROUP BY keyword, status
            """
        )

        for keyword, status, count in self.cursor.fetchall():
            keyword = keyword or ""
            status = status or ""

            if keyword not in counts:
                counts[keyword] = {
                    "total": 0,
                    "notified": 0,
                    "ignored": 0,
                    "baseline": 0,
                    "other": 0,
                }

            counts[keyword]["total"] += count

            if status in counts[keyword]:
                counts[keyword][status] += count

            else:
                counts[keyword]["other"] += count

        return counts

    def save(
        self,
        item,
        keyword,
        status="notified",
        ignore_reason=None,
    ):

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO items(
                id,
                keyword,
                title,
                price,
                url,
                status,
                ignore_reason
            )
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item.id,
                keyword,
                item.title,
                item.price,
                item.url,
                status,
                ignore_reason,
            )
        )

        self.conn.commit()

    def save_baseline_item_id(
        self,
        item_id,
        keyword,
        url,
    ):

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO items(
                id,
                keyword,
                title,
                price,
                url,
                status,
                ignore_reason
            )
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item_id,
                keyword,
                None,
                None,
                url,
                "baseline",
                "startup_baseline",
            )
        )

        self.conn.commit()

    def save_baseline_item_ids(
        self,
        baseline_items,
        keyword,
    ):
        if not baseline_items:
            return 0

        rows = [
            (
                item_id,
                keyword,
                None,
                None,
                url,
                "baseline",
                "startup_baseline",
            )
            for item_id, url in baseline_items
        ]

        self.cursor.executemany(
            """
            INSERT OR IGNORE INTO items(
                id,
                keyword,
                title,
                price,
                url,
                status,
                ignore_reason
            )
            VALUES(?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

        self.conn.commit()

        return self.cursor.rowcount

    def close(self):
        self.conn.close()
