"""
CSV file processing and validation
"""
import pandas as pd
import hashlib
from typing import Tuple, Optional, Dict
import io


class CSVProcessor:
    """Handle CSV file operations"""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.file_hash: Optional[str] = None
        
    def load_csv(self, file) -> Tuple[bool, str]:
        """
        Load and validate CSV file
        
        Args:
            file: Uploaded file object
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Try different delimiters
            delimiters = [',', ';', '\t']
            df = None
            
            for delimiter in delimiters:
                try:
                    file.seek(0)
                    df = pd.read_csv(file, delimiter=delimiter)
                    if df.shape[1] > 1:  # Valid if more than 1 column
                        break
                except:
                    continue
            
            if df is None or df.empty:
                return False, "Unable to parse CSV file. Please check the format."
            
            self.df = df
            
            # Generate file hash for caching
            file.seek(0)
            self.file_hash = hashlib.md5(file.read()).hexdigest()
            
            return True, f"Successfully loaded CSV with {df.shape[0]} rows and {df.shape[1]} columns"
            
        except Exception as e:
            return False, f"Error loading CSV: {str(e)}"
    
    def get_basic_info(self) -> Dict:
        """
        Get basic information about the dataset
        
        Returns:
            Dictionary with dataset information
        """
        if self.df is None:
            return {}
        
        return {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "dtypes": self.df.dtypes.to_dict(),
            "missing_values": self.df.isnull().sum().to_dict(),
            "memory_usage": self.df.memory_usage(deep=True).sum()
        }
    
    def get_statistical_summary(self) -> str:
        """
        Get statistical summary of the dataset
        
        Returns:
            String representation of summary statistics
        """
        if self.df is None:
            return ""
        
        summary = []
        summary.append(f"Dataset Shape: {self.df.shape[0]} rows x {self.df.shape[1]} columns\n")
        summary.append(f"Columns: {', '.join(self.df.columns)}\n")
        summary.append("\nNumerical Summary:\n")
        summary.append(self.df.describe().to_string())
        
        return "\n".join(summary)
    
    def get_sample_rows(self, n: int = 5) -> str:
        """
        Get sample rows from dataset
        
        Args:
            n: Number of rows to retrieve
            
        Returns:
            String representation of sample rows
        """
        if self.df is None:
            return ""
        
        return self.df.head(n).to_string()
    
    def get_column_info(self) -> str:
        """
        Get detailed column information
        
        Returns:
            String with column details
        """
        if self.df is None:
            return ""
        
        info = []
        for col in self.df.columns:
            dtype = self.df[col].dtype
            unique_count = self.df[col].nunique()
            null_count = self.df[col].isnull().sum()
            info.append(f"- {col}: {dtype}, {unique_count} unique values, {null_count} nulls")
        
        return "\n".join(info)
    
    def execute_pandas_code(self, code: str) -> str:
        """
        Execute pandas code on the dataframe
        
        Args:
            code: Python code to execute
            
        Returns:
            Result as string
        """
        if self.df is None:
            return "No dataset loaded"
        
        try:
            # Create local namespace with df
            local_vars = {'df': self.df, 'pd': pd}
            
            # Execute code
            result = eval(code, {"__builtins__": {}}, local_vars)
            
            # Convert result to string
            if isinstance(result, pd.DataFrame):
                return result.to_string()
            elif isinstance(result, pd.Series):
                return result.to_string()
            else:
                return str(result)
                
        except Exception as e:
            return f"Error executing code: {str(e)}"
    
    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Get the loaded dataframe"""
        return self.df
    
    def get_file_hash(self) -> Optional[str]:
        """Get the file hash for caching"""
        return self.file_hash