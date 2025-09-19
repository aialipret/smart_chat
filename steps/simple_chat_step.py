from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from services.llm_factory import llm_factory
from tools.bank_account_tool import create_bank_account
from .base_step import BaseStep
import re

class SimpleChatStep(BaseStep):
    """Simple chat step that handles tool calls manually"""
    
    def __init__(self):
        super().__init__()
        self.llm = llm_factory.get_chat_llm()
        self.tools = {"create_bank_account": create_bank_account}
    
    def execute(self, context):
        """Execute simple chat processing with manual tool handling"""
        self.validate_input(context, ['prepared_messages'])
        
        self.log_step("Processing through simple chat")
        
        try:
            messages = context['prepared_messages']
            
            # Get LLM response
            response = self.llm.invoke(messages)
            
            # Check if the response mentions bank account creation
            user_message = ""
            for msg in messages:
                if hasattr(msg, 'content') and msg.content:
                    if isinstance(msg, HumanMessage):
                        user_message = msg.content
                        break
            
            # Simple tool detection
            if self._should_create_account(user_message, response.content):
                # Extract information and call tool
                tool_result = self._handle_bank_account_creation(user_message)
                if tool_result:
                    response_content = tool_result
                else:
                    response_content = response.content
            else:
                response_content = response.content
            
            # Store results
            context['agent_response'] = response_content
            context['full_conversation'] = messages + [AIMessage(content=response_content)]
            context['success'] = True
            
            self.log_step("Simple chat processing completed")
            
        except Exception as e:
            error_msg = f"Simple chat error: {str(e)}"
            self.log_step(error_msg)
            
            # Fallback response
            context['agent_response'] = f"I apologize, but I encountered an error: {str(e)}"
            context['success'] = False
            context['error'] = error_msg
        
        return context
    
    def _should_create_account(self, user_message, response_content):
        """Check if we should create a bank account"""
        keywords = ['bank account', 'create account', 'open account', 'account creation']
        text_to_check = (user_message + " " + response_content).lower()
        
        return any(keyword in text_to_check for keyword in keywords)
    
    def _handle_bank_account_creation(self, user_message):
        """Extract info and create bank account"""
        try:
            # Simple regex to extract name, second name, and ID
            # Look for patterns like "name surname age id" or "name surname id"
            
            # Try to extract information
            name_match = re.search(r'(?:name|called|i\'m)\s+(\w+)', user_message.lower())
            
            # Look for pattern: word word number number (name surname age id)
            parts = user_message.split()
            
            if len(parts) >= 4:
                # Try to find name, surname, and ID
                potential_name = None
                potential_surname = None
                potential_id = None
                
                # Look for two consecutive words (likely name and surname)
                for i in range(len(parts) - 1):
                    if parts[i].isalpha() and parts[i+1].isalpha():
                        potential_name = parts[i]
                        potential_surname = parts[i+1]
                        break
                
                # Look for a long number (likely ID)
                for part in parts:
                    if part.isdigit() and len(part) >= 6:
                        potential_id = part
                        break
                
                if potential_name and potential_surname and potential_id:
                    result = create_bank_account.invoke({
                        "name": potential_name,
                        "second_name": potential_surname, 
                        "id_number": potential_id
                    })
                    return result
            
            return "I'd be happy to help you create a bank account! Please provide your first name, last name, and ID number in a clear format."
            
        except Exception as e:
            return f"I encountered an error while trying to create your account: {str(e)}"