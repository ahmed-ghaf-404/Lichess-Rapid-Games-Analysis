import sqlite3
from pathlib import Path


class UserStore:
    def __init__(self, db_path="data/users.db"):
        self.db_path = Path(db_path)
        self.conn = sqlite3.connect(self.db_path)
        self._create_table()

    # -------------------------
    # SETUP
    # -------------------------
    def _create_table(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            status TEXT NOT NULL
        )
        """)

        self.conn.commit()

    # -------------------------
    # HELPERS
    # -------------------------
    def _normalize(self, username: str):
        return username.lower().strip()

    # -------------------------
    # CORE OPERATIONS
    # -------------------------
    def add_pending(self, username: str):
        username = self._normalize(username)

        cursor = self.conn.cursor()

        try:
            cursor.execute("""
                INSERT INTO users (username, status)
                VALUES (?, 'pending')
            """, (username,))
            self.conn.commit()
            return True

        except sqlite3.IntegrityError:
            return False  # already exists

    def add_many_pending(self, usernames):
        new = []

        for u in usernames:
            if not u:
                continue

            u = self._normalize(u)

            if self.add_pending(u):
                new.append(u)

        return new

    def get_next_pending(self):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT username FROM users
            WHERE status = 'pending'
            ORDER BY rowid ASC
            LIMIT 1
        """)

        row = cursor.fetchone()

        if not row:
            return None

        username = row[0]

        # mark as "processing" immediately
        cursor.execute("""
            UPDATE users
            SET status = 'processing'
            WHERE username = ?
        """, (username,))

        self.conn.commit()

        return username

    def mark_processed(self, username: str):
        username = self._normalize(username)

        cursor = self.conn.cursor()

        cursor.execute("""
            UPDATE users
            SET status = 'processed'
            WHERE username = ?
        """, (username,))

        self.conn.commit()

    def get_state(self):
        cursor = self.conn.cursor()

        cursor.execute("SELECT username, status FROM users")

        rows = cursor.fetchall()

        return {
            "pending": [r[0] for r in rows if r[1] == "pending"],
            "processed": [r[0] for r in rows if r[1] == "processed"]
        }
    
    def is_processed(self, username: str):
        username = self._normalize(username)

        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT 1 FROM users
            WHERE username = ? AND status = 'processed'
        """, (username,))

        return cursor.fetchone() is not None
    
    def get_pending_batch(self, batch_size=5):
        cursor = self.conn.cursor()

        cursor.execute("""
            SELECT username FROM users
            WHERE status = 'pending'
            ORDER BY rowid ASC
            LIMIT ?
        """, (batch_size,))

        rows = cursor.fetchall()

        usernames = [r[0] for r in rows]

        # mark them as processing
        for username in usernames:
            cursor.execute("""
                UPDATE users
                SET status = 'processing'
                WHERE username = ?
            """, (username,))

        self.conn.commit()

        return usernames


    def pending_count(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users WHERE status='pending'")
        return cursor.fetchone()[0]