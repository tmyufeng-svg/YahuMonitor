import sqlite3


class Database:

    def __init__(self, db_name="items.db"):

        self.conn = sqlite3.connect(db_name)

        self.cursor = self.conn.cursor()

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

        self.conn.commit()

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

    def close(self):
        self.conn.close()
