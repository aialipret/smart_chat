"""
Pipeline Manager - Coordinates config and chat pipelines
"""

from pipelines.config_pipeline import ConfigPipeline
from pipelines.chat_pipeline import ChatPipeline

class PipelineManager:
    """Main pipeline manager that coordinates config and chat pipelines"""
    
    def __init__(self):
        print("🔧 Initializing Pipeline Manager...")
        
        # Initialize both pipelines
        self.config_pipeline = ConfigPipeline()
        self.chat_pipeline = ChatPipeline()
        
        print("✓ Pipeline Manager initialized")
    
    # Public methods that delegate to the appropriate pipeline
    def process_config(self, user_input):
        """Process config generation through Config Pipeline"""
        return self.config_pipeline.process(user_input)
    
    def process_chat(self, user_message, system_prompt=None):
        """Process chat message through Chat Pipeline"""
        return self.chat_pipeline.process(user_message, system_prompt)
    
    def get_config_pipeline(self):
        """Get the config pipeline instance"""
        return self.config_pipeline
    
    def get_chat_pipeline(self):
        """Get the chat pipeline instance"""
        return self.chat_pipeline

# Global pipeline manager instance
pipeline_manager = PipelineManager()