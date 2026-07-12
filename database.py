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
                source TEXT,
                source_item_id TEXT,
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

        self._ensure_column("source", "TEXT")
        self._ensure_column("source_item_id", "TEXT")
        self._ensure_column("keyword", "TEXT")
        self._ensure_column("title", "TEXT")
        self._ensure_column("price", "INTEGER")
        self._ensure_column("url", "TEXT")
        self._ensure_column("status", "TEXT")
        self._ensure_column("ignore_reason", "TEXT")
        self._ensure_column("first_seen", "TEXT")

        self._create_indexes()
        self._backfill_source("yahoo")
        self._backfill_source_item_id()

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
            CREATE INDEX IF NOT EXISTS idx_items_source
            ON items(source)
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_items_source_keyword
            ON items(source, keyword)
            """
        )

        self.cursor.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_items_source_item_id
            ON items(source, source_item_id)
            """
        )

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

    def _backfill_source(self, source):

        self.cursor.execute(
            """
            UPDATE items
            SET source=?
            WHERE source IS NULL OR source=''
            """,
            (source,),
        )

    def _backfill_source_item_id(self):

        self.cursor.execute(
            """
            UPDATE items
            SET source_item_id=id
            WHERE source_item_id IS NULL OR source_item_id=''
            """
        )

    def storage_id(self, item_id, source):
        if source == "yahoo":
            return item_id

        return f"{source}:{item_id}"

    def exists(self, item_id, source="yahoo"):

        self.cursor.execute(
            """
            SELECT 1
            FROM items
            WHERE source=? AND source_item_id=?
            """,
            (source, item_id),
        )

        return self.cursor.fetchone() is not None

    def get_existing_ids(self, item_ids, source="yahoo"):
        if not item_ids:
            return set()

        placeholders = ", ".join(
            "?"
            for _ in item_ids
        )

        self.cursor.execute(
            f"""
            SELECT source_item_id
            FROM items
            WHERE source=?
            AND source_item_id IN ({placeholders})
            """,
            (source, *tuple(item_ids)),
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
                source,
                keyword,
                status,
                COUNT(*)
            FROM items
            GROUP BY source, keyword, status
            """
        )

        for source, keyword, status, count in self.cursor.fetchall():
            source = source or ""
            keyword = keyword or ""
            status = status or ""
            source_keyword = (
                f"{source}:{keyword}"
                if source
                else keyword
            )

            if source_keyword not in counts:
                counts[source_keyword] = {
                    "source": source,
                    "keyword": keyword,
                    "total": 0,
                    "notified": 0,
                    "ignored": 0,
                    "baseline": 0,
                    "other": 0,
                }

            counts[source_keyword]["total"] += count

            if status in counts[source_keyword]:
                counts[source_keyword][status] += count

            else:
                counts[source_keyword]["other"] += count

        return counts

    def save(
        self,
        item,
        keyword,
        source="yahoo",
        status="notified",
        ignore_reason=None,
    ):

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO items(
                id,
                source,
                source_item_id,
                keyword,
                title,
                price,
                url,
                status,
                ignore_reason
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.storage_id(item.id, source),
                source,
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
        source="yahoo",
    ):

        self.cursor.execute(
            """
            INSERT OR IGNORE INTO items(
                id,
                source,
                source_item_id,
                keyword,
                title,
                price,
                url,
                status,
                ignore_reason
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.storage_id(item_id, source),
                source,
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
        source="yahoo",
    ):
        if not baseline_items:
            return 0

        rows = [
            (
                self.storage_id(item_id, source),
                source,
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
                source,
                source_item_id,
                keyword,
                title,
                price,
                url,
                status,
                ignore_reason
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )

        self.conn.commit()

        return self.cursor.rowcount

    def close(self):
        self.conn.close()
