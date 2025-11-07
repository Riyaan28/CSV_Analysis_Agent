"""
Ollama client for LLM integration
"""
import os
from typing import List, Optional
import ollama


class OllamaClient:
    """Client to interact with Ollama service"""
    
    def __init__(self, model_name: str = "llama3.2"):
        """
        Initialize Ollama client
        
        Args:
            model_name: Name of the Ollama model to use
        """
        self.model_name = model_name
        self.ollama_host = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        
        # Create ollama client with explicit host
        self.client = ollama.Client(host=self.ollama_host)
        print(f"🔗 Configured Ollama at: {self.ollama_host}")
        
    def check_availability(self) -> bool:
        """
        Check if Ollama service is available
        
        Returns:
            bool: True if available, False otherwise
        """
        try:
            self.client.list()
            print(f"✅ Ollama connected successfully at {self.ollama_host}")
            return True
        except Exception as e:
            print(f"❌ Ollama not available at {self.ollama_host}: {str(e)}")
            return False
    
    def list_models(self) -> List[str]:
        """
        Get list of available models
        
        Returns:
            List of model names
        """
        try:
            models = self.client.list()
            # Extract model names correctly
            if isinstance(models, dict) and 'models' in models:
                return [model['name'] for model in models['models']]
            return []
        except Exception as e:
            print(f"Error listing models: {str(e)}")
            return []
    
    def generate(self, prompt: str, context: Optional[str] = None) -> str:
        """
        Generate response from Ollama
        
        Args:
            prompt: User query
            context: Additional context for the query
            
        Returns:
            Generated response
        """
        try:
            full_prompt = prompt
            if context:
                full_prompt = f"Context:\n{context}\n\nQuery: {prompt}"
            
            response = self.client.generate(
                model=self.model_name,
                prompt=full_prompt
            )
            return response['response']
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def chat(self, messages: List[dict]) -> str:
        """
        Chat with Ollama using message history
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            
        Returns:
            Generated response
        """
        try:
            response = self.client.chat(
                model=self.model_name,
                messages=messages
            )
            return response['message']['content']
        except Exception as e:
            return f"Error in chat: {str(e)}"