"""
Cache management using SQLite
"""
import sqlite3
import hashlib
import json
from datetime import datetime
from typing import Optional, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer


class CacheManager:
    """Manage query caching with SQLite"""
    
    def __init__(self, db_path: str = "cache.db", similarity_threshold: float = 0.9):
        """
        Initialize cache manager
        
        Args:
            db_path: Path to SQLite database
            similarity_threshold: Threshold for query similarity
        """
        self.db_path = db_path
        self.similarity_threshold = similarity_threshold
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS query_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_hash TEXT NOT NULL,
                query_text TEXT NOT NULL,
                query_embedding TEXT NOT NULL,
                dataset_hash TEXT NOT NULL,
                response TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_query_hash 
            ON query_cache(query_hash, dataset_hash)
        """)
        
        conn.commit()
        conn.close()
    
    def _compute_query_hash(self, query: str, dataset_hash: str) -> str:
        """
        Compute hash for query and dataset combination
        
        Args:
            query: User query
            dataset_hash: Hash of the dataset
            
        Returns:
            MD5 hash string
        """
        combined = f"{query.lower().strip()}_{dataset_hash}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Similarity score
        """
        dot_product = np.dot(embedding1, embedding2)
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def get_cached_response(self, query: str, dataset_hash: str) -> Tuple[Optional[str], bool]:
        """
        Get cached response for a query
        
        Args:
            query: User query
            dataset_hash: Hash of current dataset
            
        Returns:
            Tuple of (response, is_cache_hit)
        """
        query_normalized = query.lower().strip()
        query_hash = self._compute_query_hash(query_normalized, dataset_hash)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # First, try exact hash match
        cursor.execute("""
            SELECT response FROM query_cache 
            WHERE query_hash = ? AND dataset_hash = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (query_hash, dataset_hash))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return result[0], True
        
        # If no exact match, try semantic similarity
        query_embedding = self.encoder.encode([query_normalized])[0]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT query_embedding, response FROM query_cache 
            WHERE dataset_hash = ?
        """, (dataset_hash,))
        
        rows = cursor.fetchall()
        conn.close()
        
        for row in rows:
            cached_embedding = np.array(json.loads(row[0]))
            similarity = self._compute_similarity(query_embedding, cached_embedding)
            
            if similarity >= self.similarity_threshold:
                return row[1], True
        
        return None, False
    
    def cache_response(self, query: str, dataset_hash: str, response: str):
        """
        Cache a query response
        
        Args:
            query: User query
            dataset_hash: Hash of the dataset
            response: Response to cache
        """
        query_normalized = query.lower().strip()
        query_hash = self._compute_query_hash(query_normalized, dataset_hash)
        query_embedding = self.encoder.encode([query_normalized])[0]
        embedding_json = json.dumps(query_embedding.tolist())
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO query_cache 
            (query_hash, query_text, query_embedding, dataset_hash, response)
            VALUES (?, ?, ?, ?, ?)
        """, (query_hash, query, embedding_json, dataset_hash, response))
        
        conn.commit()
        conn.close()
    
    def clear_cache(self):
        """Clear all cached entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM query_cache")
        conn.commit()
        conn.close()
    
    def get_cache_stats(self) -> dict:
        """
        Get cache statistics
        
        Returns:
            Dictionary with cache stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM query_cache")
        total_entries = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_entries": total_entries
        }