"""
Unit tests for CSV Analysis Agent
"""
import unittest
import pandas as pd
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.csv_processor import CSVProcessor
from src.rag_module import RAGModule
from src.cache_manager import CacheManager
from src.feedback_manager import FeedbackManager


class TestCSVProcessor(unittest.TestCase):
    """Test CSV processing functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.processor = CSVProcessor()
        
        # Create test dataframe
        self.test_data = {
            'name': ['John', 'Jane', 'Bob'],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000]
        }
        self.test_df = pd.DataFrame(self.test_data)
    
    def test_get_basic_info(self):
        """Test basic info extraction"""
        self.processor.df = self.test_df
        info = self.processor.get_basic_info()
        
        self.assertEqual(info['shape'], (3, 3))
        self.assertEqual(len(info['columns']), 3)
        self.assertIn('name', info['columns'])
    
    def test_get_statistical_summary(self):
        """Test statistical summary"""
        self.processor.df = self.test_df
        summary = self.processor.get_statistical_summary()
        
        self.assertIn('Dataset Shape', summary)
        self.assertIn('Columns', summary)
    
    def test_get_sample_rows(self):
        """Test sample rows retrieval"""
        self.processor.df = self.test_df
        sample = self.processor.get_sample_rows(2)
        
        self.assertIsNotNone(sample)
        self.assertIn('John', sample)


class TestRAGModule(unittest.TestCase):
    """Test RAG functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.rag = RAGModule()
        
        self.test_data = {
            'name': ['John', 'Jane', 'Bob'],
            'age': [25, 30, 35],
            'salary': [50000, 60000, 70000]
        }
        self.test_df = pd.DataFrame(self.test_data)
    
    def test_build_index(self):
        """Test index building"""
        self.rag.build_index(self.test_df)
        
        self.assertIsNotNone(self.rag.index)
        self.assertGreater(len(self.rag.documents), 0)
    
    def test_retrieve_context(self):
        """Test context retrieval"""
        self.rag.build_index(self.test_df)
        docs, distances = self.rag.retrieve_context("What are the columns?", top_k=3)
        
        self.assertGreater(len(docs), 0)
        self.assertEqual(len(docs), len(distances))


class TestCacheManager(unittest.TestCase):
    """Test caching functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.cache = CacheManager(db_path=":memory:")
    
    def test_cache_and_retrieve(self):
        """Test caching and retrieval"""
        query = "What is the average salary?"
        dataset_hash = "test_hash_123"
        response = "The average salary is 60000"
        
        # Cache response
        self.cache.cache_response(query, dataset_hash, response)
        
        # Retrieve response
        cached, hit = self.cache.get_cached_response(query, dataset_hash)
        
        self.assertTrue(hit)
        self.assertEqual(cached, response)
    
    def test_cache_miss(self):
        """Test cache miss"""
        cached, hit = self.cache.get_cached_response(
            "Nonexistent query",
            "nonexistent_hash"
        )
        
        self.assertFalse(hit)
    
    def test_clear_cache(self):
        """Test cache clearing"""
        self.cache.cache_response("query", "hash", "response")
        self.cache.clear_cache()
        
        stats = self.cache.get_cache_stats()
        self.assertEqual(stats['total_entries'], 0)


class TestFeedbackManager(unittest.TestCase):
    """Test feedback management"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.feedback = FeedbackManager(db_path=":memory:")
    
    def test_add_feedback(self):
        """Test adding feedback"""
        success = self.feedback.add_feedback(
            query="Test query",
            response="Test response",
            rating="positive",
            feedback_text="Great answer!"
        )
        
        self.assertTrue(success)
    
    def test_get_feedback_stats(self):
        """Test feedback statistics"""
        self.feedback.add_feedback("q1", "r1", "positive")
        self.feedback.add_feedback("q2", "r2", "negative")
        
        stats = self.feedback.get_feedback_stats()
        
        self.assertEqual(stats['total'], 2)
        self.assertEqual(stats['positive'], 1)
        self.assertEqual(stats['negative'], 1)


if __name__ == '__main__':
    unittest.main()