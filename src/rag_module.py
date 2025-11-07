"""
RAG (Retrieval-Augmented Generation) implementation using FAISS
"""
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional
import pandas as pd


class RAGModule:
    """RAG implementation for context retrieval"""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize RAG module
        
        Args:
            model_name: Sentence transformer model name
        """
        self.encoder = SentenceTransformer(model_name)
        self.index: Optional[faiss.Index] = None
        self.documents: List[str] = []
        self.dimension = 384  # Dimension for all-MiniLM-L6-v2
        
    def build_index(self, df: pd.DataFrame):
        """
        Build FAISS index from dataframe
        
        Args:
            df: Pandas dataframe to index
        """
        try:
            self.documents = []
            
            print(f"Building index for dataframe with shape {df.shape}")
            
            # Add column information
            for col in df.columns:
                dtype = df[col].dtype
                unique_count = df[col].nunique()
                null_count = df[col].isnull().sum()
                
                doc = f"Column: {col}, Type: {dtype}, Unique values: {unique_count}, Null count: {null_count}"
                
                # Add sample values for categorical columns
                if df[col].nunique() < 20:
                    sample_values = df[col].dropna().unique()[:5]
                    doc += f", Sample values: {', '.join(map(str, sample_values))}"
                
                self.documents.append(doc)
            
            print(f"Added {len(self.documents)} column documents")
            
            # Add statistical summary for numerical columns
            numerical_cols = df.select_dtypes(include=[np.number]).columns
            for col in numerical_cols:
                stats = df[col].describe()
                doc = f"Statistics for {col}: mean={stats['mean']:.2f}, std={stats['std']:.2f}, min={stats['min']:.2f}, max={stats['max']:.2f}"
                self.documents.append(doc)
            
            # Add sample rows
            for idx, row in df.head(3).iterrows():
                row_str = ", ".join([f"{col}={val}" for col, val in row.items()])
                self.documents.append(f"Sample row {idx}: {row_str}")
            
            # Add correlation information for numerical columns
            if len(numerical_cols) > 1:
                corr_matrix = df[numerical_cols].corr()
                for i, col1 in enumerate(numerical_cols):
                    for col2 in numerical_cols[i+1:]:
                        corr_value = corr_matrix.loc[col1, col2]
                        if abs(corr_value) > 0.5:
                            self.documents.append(
                                f"Correlation between {col1} and {col2}: {corr_value:.2f}"
                            )
            
            print(f"Total documents: {len(self.documents)}")
            print("Creating embeddings...")
            
            # Create embeddings
            embeddings = self.encoder.encode(self.documents, show_progress_bar=False)
            embeddings = np.array(embeddings).astype('float32')
            
            print("Building FAISS index...")
            
            # Create FAISS index
            self.index = faiss.IndexFlatL2(self.dimension)
            self.index.add(embeddings)
            
            print("FAISS index built successfully")
            
        except Exception as e:
            print(f"Error building index: {str(e)}")
            raise
        
    def retrieve_context(self, query: str, top_k: int = 5) -> Tuple[List[str], List[float]]:
        """
        Retrieve relevant context for a query
        
        Args:
            query: User query
            top_k: Number of top results to retrieve
            
        Returns:
            Tuple of (relevant documents, distances)
        """
        if self.index is None or len(self.documents) == 0:
            return [], []
        
        # Encode query
        query_embedding = self.encoder.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        
        # Search
        top_k = min(top_k, len(self.documents))
        distances, indices = self.index.search(query_embedding, top_k)
        
        # Get relevant documents
        relevant_docs = [self.documents[idx] for idx in indices[0]]
        relevant_distances = distances[0].tolist()
        
        return relevant_docs, relevant_distances
    
    def get_context_string(self, query: str, top_k: int = 5) -> str:
        """
        Get formatted context string for a query
        
        Args:
            query: User query
            top_k: Number of contexts to retrieve
            
        Returns:
            Formatted context string
        """
        docs, distances = self.retrieve_context(query, top_k)
        
        if not docs:
            return ""
        
        context_parts = ["Relevant Dataset Information:"]
        for i, (doc, dist) in enumerate(zip(docs, distances)):
            context_parts.append(f"{i+1}. {doc}")
        
        return "\n".join(context_parts)