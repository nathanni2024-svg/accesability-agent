import os
import sqlite3
import numpy as np
from datetime import datetime

_embedding_model = None

def _get_embedding_model():
    """Lazy-loads the embedding model only when needed to save memory and startup time."""
    global _embedding_model
    if _embedding_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            # Initialize the small, fast local model for M5 inference
            _embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        except ImportError:
            pass
    return _embedding_model

from config import SQLITE_DB_PATH, ensure_app_directories

ensure_app_directories()
DATABASE_FILE = str(SQLITE_DB_PATH)
OLD_BRAIN_DIR = "AI_Brain"

def _get_db_type():
    """Returns whether we are using an online PostgreSQL database or local SQLite."""
    return "postgresql" if os.getenv("DATABASE_URL") else "sqlite"

def _get_connection():
    """Creates a database connection (PostgreSQL or local SQLite)."""
    db_url = os.getenv("DATABASE_URL")
    if db_url:
        import psycopg2
        # Support postgres:// URL schemes (which some hosts return instead of postgresql://)
        if db_url.startswith("postgres://"):
            db_url = db_url.replace("postgres://", "postgresql://", 1)
        return psycopg2.connect(db_url)
    else:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        # Enable WAL mode for better concurrent performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=-64000")
        return conn

def _execute_write(query, params=()):
    """Executes an SQL write query (handles placeholder differences)."""
    db_type = _get_db_type()
    conn = _get_connection()
    cursor = conn.cursor()
    if db_type == "postgresql":
        query = query.replace("?", "%s")
    cursor.execute(query, params)
    conn.commit()
    conn.close()

def _execute_read_all(query, params=()):
    """Executes a read query and returns a standardized list of dicts."""
    db_type = _get_db_type()
    conn = _get_connection()
    cursor = conn.cursor()
    if db_type == "postgresql":
        query = query.replace("?", "%s")
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        results.append({
            'topic': r[0],
            'information': r[1],
            'embedding': bytes(r[2]) if r[2] is not None else None,
            'created_at': r[3]
        })
    conn.close()
    return results

def _init_db():
    """Builds the memories SQL architecture with online/local fallback."""
    db_type = _get_db_type()
    conn = _get_connection()
    cursor = conn.cursor()
    if db_type == "postgresql":
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                topic VARCHAR(255) PRIMARY KEY,
                information TEXT NOT NULL,
                embedding BYTEA,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memories (
                topic TEXT PRIMARY KEY,
                information TEXT NOT NULL,
                embedding BLOB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.commit()
    conn.close()

def _migrate_old_files():
    """If the legacy text folder exists, suck it into SQL and safely delete it."""
    if not os.path.exists(OLD_BRAIN_DIR):
        return
        
    migrated_any = False
    
    if os.path.isdir(OLD_BRAIN_DIR):
        for filename in os.listdir(OLD_BRAIN_DIR):
            if filename.endswith(".txt"):
                filepath = os.path.join(OLD_BRAIN_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        topic = filename.replace('.txt', '')
                        
                        embedding_blob = None
                        model = _get_embedding_model()
                        if model:
                            embedding = model.encode(content).astype(np.float32).tobytes()
                            embedding_blob = embedding
                            
                        _execute_write('''
                            INSERT INTO memories (topic, information, embedding) 
                            VALUES (?, ?, ?)
                            ON CONFLICT(topic) DO UPDATE SET 
                                information=EXCLUDED.information,
                                embedding=EXCLUDED.embedding
                        ''', (topic, content, embedding_blob))
                        migrated_any = True
                    os.remove(filepath)
                except Exception:
                    pass
                
        try:
            os.rmdir(OLD_BRAIN_DIR)
        except OSError:
            pass

_init_db()
_migrate_old_files()

def teach_ai(topic: str, information: str) -> str:
    """
    Executes an SQL Upsert with locally-generated embeddings for semantic retrieval.
    """
    clean_topic = topic.replace("..", "").replace("/", "_").strip()
    
    try:
        embedding_blob = None
        model = _get_embedding_model()
        if model:
            embedding = model.encode(information).astype(np.float32).tobytes()
            embedding_blob = embedding

        _execute_write('''
            INSERT INTO memories (topic, information, embedding) 
            VALUES (?, ?, ?)
            ON CONFLICT(topic) DO UPDATE SET 
                information=EXCLUDED.information, 
                embedding=EXCLUDED.embedding,
                created_at=CURRENT_TIMESTAMP
        ''', (clean_topic, information, embedding_blob))
        return f"🧠 SQL Database Updated: Learned permanent rule about '{topic}' (Online Sync Enabled)."
    except Exception as e:
        return f"❌ SQL Error updating AI memory: {str(e)}"

def recall_memory(query: str = None) -> str:
    """
    Retrieves memories. If a query is provided, performs semantic search via cosine similarity.
    Otherwise, returns all records (fallback).
    """
    try:
        rows = _execute_read_all('SELECT topic, information, embedding, created_at FROM memories')
        
        if not rows:
            return ""
            
        model = _get_embedding_model()
        if query and model:
            query_embedding = model.encode(query).astype(np.float32)
            
            scored_memories = []
            for row in rows:
                if row['embedding']:
                    mem_embedding = np.frombuffer(row['embedding'], dtype=np.float32)
                    similarity = np.dot(query_embedding, mem_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(mem_embedding)
                    )
                    scored_memories.append((similarity, row))
                else:
                    scored_memories.append((0.0, row))
            
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            top_memories = [m[1] for m in scored_memories[:5] if m[0] > 0.3]
            
            if not top_memories:
                return ""
                
            brain_data = []
            for row in top_memories:
                brain_data.append(f"--- Relevant Context: {row['topic']} (Stored: {row['created_at']}) ---\n{row['information']}\n")
            return "\n[RELEVANT LONG-TERM MEMORY RECALLED]\n" + "\n".join(brain_data)
        
        else:
            brain_data = []
            for row in rows:
                brain_data.append(f"--- Permanent Rule/Context: {row['topic']} (Stored: {row['created_at']}) ---\n{row['information']}\n")
            return "\n" + "\n".join(brain_data)
            
    except Exception as e:
        print(f"Recall error: {e}")
        return ""

def count_brain_files() -> int:
    """Runs an ultra-fast SELECT COUNT(*) query to power the UI indicator."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM memories')
        row = cursor.fetchone()
        conn.close()
        if row:
            return row[0]
        return 0
    except Exception:
        return 0
