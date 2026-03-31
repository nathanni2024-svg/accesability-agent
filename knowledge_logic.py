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

def _get_connection():
    """Creates a local connection to the AI SQL Database with M5-optimized performance."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for better concurrent performance on Apple Silicon SSDs
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000") # 64MB Cache
    return conn

def _init_db():
    """Builds the AI_Brain SQL architecture with embedding support."""
    conn = _get_connection()
    cursor = conn.cursor()
    # Create main table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            topic TEXT PRIMARY KEY,
            information TEXT NOT NULL,
            embedding BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Migration: Add embedding column if it doesn't exist (for existing DBs)
    try:
        cursor.execute('ALTER TABLE memories ADD COLUMN embedding BLOB')
    except sqlite3.OperationalError:
        pass # Column already exists
        
    conn.commit()
    conn.close()

def _migrate_old_files():
    """If the legacy text folder exists, suck it into SQL and safely delete it."""
    if not os.path.exists(OLD_BRAIN_DIR):
        return
        
    conn = _get_connection()
    cursor = conn.cursor()
    
    migrated_any = False
    
    if os.path.isdir(OLD_BRAIN_DIR):
        for filename in os.listdir(OLD_BRAIN_DIR):
            if filename.endswith(".txt"):
                filepath = os.path.join(OLD_BRAIN_DIR, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        content = f.read()
                        topic = filename.replace('.txt', '')
                        
                        # Generate embedding for legacy data
                        embedding_blob = None
                        model = _get_embedding_model()
                        if model:
                            embedding = model.encode(content).astype(np.float32).tobytes()
                            embedding_blob = embedding
                            
                        cursor.execute('''
                            INSERT INTO memories (topic, information, embedding) 
                            VALUES (?, ?, ?)
                            ON CONFLICT(topic) DO UPDATE SET 
                                information=excluded.information,
                                embedding=excluded.embedding
                        ''', (topic, content, embedding_blob))
                        migrated_any = True
                    os.remove(filepath)
                except Exception:
                    pass
                
        if migrated_any:
            conn.commit()
        
        try:
            os.rmdir(OLD_BRAIN_DIR)
        except OSError:
            pass
            
    conn.close()

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
            # Generate embedding locally on M5 chip
            embedding = model.encode(information).astype(np.float32).tobytes()
            embedding_blob = embedding

        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO memories (topic, information, embedding) 
            VALUES (?, ?, ?)
            ON CONFLICT(topic) DO UPDATE SET 
                information=excluded.information, 
                embedding=excluded.embedding,
                created_at=CURRENT_TIMESTAMP
        ''', (clean_topic, information, embedding_blob))
        conn.commit()
        conn.close()
        return f"🧠 SQL Database Updated: Learned permanent rule about '{topic}' locally (Semantics Enabled)."
    except Exception as e:
        return f"❌ SQL Error updating AI memory: {str(e)}"

def recall_memory(query: str = None) -> str:
    """
    Retrieves memories. If a query is provided, performs semantic search via cosine similarity.
    Otherwise, returns all records (fallback).
    """
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT topic, information, embedding, created_at FROM memories')
        rows = cursor.fetchall()
        conn.close()
        
        if not rows:
            return ""
            
        model = _get_embedding_model()
        if query and model:
            # Perform semantic cosine similarity locally
            query_embedding = model.encode(query).astype(np.float32)
            
            scored_memories = []
            for row in rows:
                if row['embedding']:
                    mem_embedding = np.frombuffer(row['embedding'], dtype=np.float32)
                    # Simple cosine similarity (dot product of normalized vectors)
                    similarity = np.dot(query_embedding, mem_embedding) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(mem_embedding)
                    )
                    scored_memories.append((similarity, row))
                else:
                    # Low score if no embedding
                    scored_memories.append((0.0, row))
            
            # Sort by similarity and take top 5
            scored_memories.sort(key=lambda x: x[0], reverse=True)
            top_memories = [m[1] for m in scored_memories[:5] if m[0] > 0.3] # Threshold
            
            if not top_memories:
                return ""
                
            brain_data = []
            for row in top_memories:
                brain_data.append(f"--- Relevant Context: {row['topic']} (Stored: {row['created_at']}) ---\n{row['information']}\n")
            return "\n[RELEVANT LONG-TERM MEMORY RECALLED]\n" + "\n".join(brain_data)
        
        else:
            # Full dump fallback
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
        cursor.execute('SELECT COUNT(*) as cnt FROM memories')
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row['cnt']
        return 0
    except Exception:
        return 0

