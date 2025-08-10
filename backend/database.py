import sqlite3
import uuid

DATABASE_URL = "prompts.db"

def init_db():
    """Initializes the database and creates the prompts table if it doesn't exist."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prompts (
            id TEXT PRIMARY KEY,
            original_prompt TEXT NOT NULL,
            improved_prompt TEXT NOT NULL,
            is_public INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

def save_prompt(original_prompt: str, improved_prompt: str) -> str:
    """Saves a prompt pair to the database and returns its unique ID."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    prompt_id = str(uuid.uuid4())
    cursor.execute(
        "INSERT INTO prompts (id, original_prompt, improved_prompt) VALUES (?, ?, ?)",
        (prompt_id, original_prompt, improved_prompt)
    )
    conn.commit()
    conn.close()
    return prompt_id

def get_prompt(prompt_id: str):
    """Retrieves a prompt pair by its ID."""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prompts WHERE id = ?", (prompt_id,))
    prompt = cursor.fetchone()
    conn.close()
    return prompt

def publish_prompt(prompt_id: str):
    """Marks a prompt as public."""
    conn = sqlite3.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute("UPDATE prompts SET is_public = 1 WHERE id = ?", (prompt_id,))
    conn.commit()
    conn.close()

def get_public_prompts():
    """Retrieves all public prompts, most recent first."""
    conn = sqlite3.connect(DATABASE_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, original_prompt, improved_prompt FROM prompts WHERE is_public = 1 ORDER BY created_at DESC")
    prompts = cursor.fetchall()
    conn.close()
    return prompts
