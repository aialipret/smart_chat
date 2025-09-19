from langchain_core.messages import HumanMessage, SystemMessage
from .base_step import BaseStep

class ChatPreparationStep(BaseStep):
    """Step to prepare chat input for LangGraph agent processing"""
    
    def execute(self, context):
        """Prepare chat messages for LangGraph agent"""
        self.validate_input(context, ['user_message'])
        
        self.log_step("Preparing chat input")
        
        try:
            user_message = context['user_message']
            system_prompt = context.get('system_prompt', 'You are a helpful assistant that can create bank accounts.')
            
            # Validate inputs
            if not user_message or not user_message.strip():
                raise ValueError("User message is empty or None")
            
            # Create LangChain messages
            messages = []
            if system_prompt and system_prompt.strip():
                messages.append(SystemMessage(content=system_prompt.strip()))
            messages.append(HumanMessage(content=user_message.strip()))
            
            # Debug: Log the prepared messages
            self.log_step(f"Prepared {len(messages)} messages")
            for i, msg in enumerate(messages):
                self.log_step(f"Message {i}: {type(msg).__name__} - {msg.content[:50]}...")
            
            # Store prepared messages
            context['prepared_messages'] = messages
            context['original_user_message'] = user_message
            context['original_system_prompt'] = system_prompt
            
            self.log_step("Chat input prepared successfully")
            
        except Exception as e:
            self.log_step(f"Error preparing chat input: {str(e)}")
            raise
        
        return context