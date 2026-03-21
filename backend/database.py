import os
import sqlite3


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DB_PATH = os.path.join(BASE_DIR, "data", "document_qa.db")


def get_db_path():
    return os.getenv("DATABASE_PATH", DEFAULT_DB_PATH)


def get_connection():
    db_path = get_db_path()
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        cursor = connection.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                document_id TEXT PRIMARY KEY,
                user_id INTEGER,
                filename TEXT NOT NULL,
                filepath TEXT NOT NULL,
                text_content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS question_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (document_id) REFERENCES documents (document_id)
            )
            """
        )

        document_columns = {
            row["name"]
            for row in cursor.execute("PRAGMA table_info(documents)").fetchall()
        }
        if "user_id" not in document_columns:
            cursor.execute("ALTER TABLE documents ADD COLUMN user_id INTEGER")

        connection.commit()


def create_user(email, password_hash):
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT INTO users (email, password_hash)
            VALUES (?, ?)
            """,
            (email, password_hash),
        )
        connection.commit()
        return cursor.lastrowid


def get_user_by_email(email):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, email, password_hash, created_at
            FROM users
            WHERE email = ?
            """,
            (email,),
        ).fetchone()
    return dict(row) if row else None


def get_user_by_id(user_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT id, email, created_at
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        ).fetchone()
    return dict(row) if row else None


def save_document(document_id, user_id, filename, filepath, text_content):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO documents (document_id, user_id, filename, filepath, text_content)
            VALUES (?, ?, ?, ?, ?)
            """,
            (document_id, user_id, filename, filepath, text_content),
        )
        connection.commit()


def get_document(document_id, user_id):
    with get_connection() as connection:
        row = connection.execute(
            """
            SELECT document_id, user_id, filename, filepath, text_content, created_at
            FROM documents
            WHERE document_id = ? AND user_id = ?
            """,
            (document_id, user_id),
        ).fetchone()
    return dict(row) if row else None


def save_question_history(document_id, question, answer):
    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO question_history (document_id, question, answer)
            VALUES (?, ?, ?)
            """,
            (document_id, question, answer),
        )
        connection.commit()


def get_question_history(document_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT question, answer, created_at
            FROM question_history
            WHERE document_id = ?
            ORDER BY created_at ASC, id ASC
            """,
            (document_id,),
        ).fetchall()
    return [dict(row) for row in rows]


def list_documents(user_id):
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                d.document_id,
                d.filename,
                d.created_at,
                COUNT(q.id) AS question_count,
                MAX(q.created_at) AS last_question_at
            FROM documents d
            LEFT JOIN question_history q ON q.document_id = d.document_id
            WHERE d.user_id = ?
            GROUP BY d.document_id, d.filename, d.created_at
            ORDER BY COALESCE(MAX(q.created_at), d.created_at) DESC
            """,
            (user_id,),
        ).fetchall()
    return [dict(row) for row in rows]
