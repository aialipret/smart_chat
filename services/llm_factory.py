"""
LLM Factory for centralized LLM management
This module provides a singleton pattern for LLM instances to avoid multiple initializations.
"""

import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

class LLMFactory:
    """Singleton factory for LLM instances"""
    
    _instance = None
    _llm_instances = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LLMFactory, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.api_key = os.getenv('GOOGLE_API_KEY')
            if not self.api_key:
                raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
            self.initialized = True
    
    def get_llm(self, model_name="gemini-1.5-flash", temperature=0.7, **kwargs):
        """
        Get or create an LLM instance with specified parameters
        
        Args:
            model_name (str): The model name to use
            temperature (float): Temperature for the model
            **kwargs: Additional parameters for the model
            
        Returns:
            ChatGoogleGenerativeAI: Configured LLM instance
        """
        # Create a cache key based on parameters
        cache_key = f"{model_name}_{temperature}_{hash(frozenset(kwargs.items()))}"
        
        if cache_key not in self._llm_instances:
            print(f"🔧 Creating new LLM instance: {model_name} (temp: {temperature})")
            
            self._llm_instances[cache_key] = ChatGoogleGenerativeAI(
                model=model_name,
                temperature=temperature,
                google_api_key=self.api_key,
                **kwargs
            )
        else:
            print(f"♻️  Reusing existing LLM instance: {model_name}")
        
        return self._llm_instances[cache_key]
    
    def get_config_llm(self):
        """Get LLM optimized for configuration generation"""
        return self.get_llm(
            model_name="gemini-1.5-flash",
            temperature=0.3  # Lower temperature for more consistent JSON generation
        )
    
    def get_chat_llm(self):
        """Get LLM optimized for chat interactions"""
        return self.get_llm(
            model_name="gemini-1.5-flash",
            temperature=0.7  # Higher temperature for more creative responses
        )
    
    def clear_cache(self):
        """Clear all cached LLM instances"""
        print("🧹 Clearing LLM cache")
        self._llm_instances.clear()

# Global factory instance
llm_factory = LLMFactory()