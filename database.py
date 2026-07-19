import sqlite3

def get_connection():
    """Return a connection that behaves like a dictionary/row source."""
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db() -> None:
    """Initialize the database schema."""
    conn = get_connection()
    cur = conn.cursor()
    # Create the recruiter inquiries table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recruiter_inquiries (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL,
            company    TEXT,
            email      TEXT    NOT NULL,
            message    TEXT    NOT NULL,
            created_at TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

# Recruiter Inquiry Operations
def save_inquiry(name: str, company: str, email: str, message: str) -> None:
    """Persist a contact form message from a recruiter."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO recruiter_inquiries (name, company, email, message) VALUES (?, ?, ?, ?)",
        (name, company, email, message)
    )
    conn.commit()
    conn.close()

def get_inquiries() -> list[dict]:
    """Retrieve all recruiter inquiries ordered by newest first."""
    conn = get_connection()
    cur = conn.execute("SELECT * FROM recruiter_inquiries ORDER BY created_at DESC")
    rows = cur.fetchall()
    conn.close()
    return [
        {
            "id": r["id"],
            "name": r["name"],
            "company": r["company"],
            "email": r["email"],
            "message": r["message"],
            "created_at": r["created_at"],
        }
        for r in rows
    ]
