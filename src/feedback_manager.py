"""
Feedback management system using SQLite
"""
import sqlite3
from datetime import datetime
from typing import List, Dict
import pandas as pd


class FeedbackManager:
    """Manage user feedback"""
    
    def __init__(self, db_path: str = "feedback.db"):
        """
        Initialize feedback manager
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query_text TEXT NOT NULL,
                response_text TEXT NOT NULL,
                rating TEXT NOT NULL,
                feedback_text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_feedback(self, query: str, response: str, rating: str, 
                    feedback_text: str = "") -> bool:
        """
        Add feedback for a query-response pair
        
        Args:
            query: User query
            response: System response
            rating: 'positive' or 'negative'
            feedback_text: Optional text feedback
            
        Returns:
            Success status
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO feedback 
                (query_text, response_text, rating, feedback_text)
                VALUES (?, ?, ?, ?)
            """, (query, response, rating, feedback_text))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding feedback: {str(e)}")
            return False
    
    def get_all_feedback(self) -> List[Dict]:
        """
        Get all feedback entries
        
        Returns:
            List of feedback dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, query_text, response_text, rating, feedback_text, timestamp
            FROM feedback
            ORDER BY timestamp DESC
        """)
        
        rows = cursor.fetchall()
        conn.close()
        
        feedback_list = []
        for row in rows:
            feedback_list.append({
                "id": row[0],
                "query": row[1],
                "response": row[2],
                "rating": row[3],
                "feedback_text": row[4],
                "timestamp": row[5]
            })
        
        return feedback_list
    
    def get_feedback_stats(self) -> Dict:
        """
        Get feedback statistics
        
        Returns:
            Dictionary with feedback stats
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating = 'positive'")
        positive_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM feedback WHERE rating = 'negative'")
        negative_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_count = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total": total_count,
            "positive": positive_count,
            "negative": negative_count,
            "positive_rate": positive_count / total_count if total_count > 0 else 0
        }
    
    def export_to_csv(self, output_path: str = "feedback_export.csv") -> bool:
        """
        Export feedback to CSV file
        
        Args:
            output_path: Path for output CSV file
            
        Returns:
            Success status
        """
        try:
            feedback_list = self.get_all_feedback()
            
            if not feedback_list:
                return False
            
            df = pd.DataFrame(feedback_list)
            
            # Format timestamp to be more readable
            if 'timestamp' in df.columns:
                df['timestamp'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            
            df.to_csv(output_path, index=False, encoding='utf-8-sig')
            return True
            
        except Exception as e:
            print(f"Error exporting feedback: {str(e)}")
            return False
    
    def clear_feedback(self):
        """Clear all feedback entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM feedback")
        conn.commit()
        conn.close()