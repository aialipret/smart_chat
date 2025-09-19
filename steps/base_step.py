from abc import ABC, abstractmethod

class BaseStep(ABC):
    """Base class for all processing steps"""
    
    def __init__(self, name=None):
        self.name = name or self.__class__.__name__
    
    @abstractmethod
    def execute(self, context):
        """
        Execute the step with given context
        
        Args:
            context (dict): Context data from previous steps
            
        Returns:
            dict: Updated context with step results
        """
        pass
    
    def validate_input(self, context, required_keys):
        """Validate that required keys exist in context"""
        missing_keys = [key for key in required_keys if key not in context]
        if missing_keys:
            raise ValueError(f"Missing required keys in context: {missing_keys}")
    
    def log_step(self, message):
        """Log step execution"""
        print(f"[{self.name}] {message}")