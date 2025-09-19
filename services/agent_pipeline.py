"""
Agent-Aware Pipeline - Handles chat processing based on agent configuration
"""

import os
import json
import re
from datetime import datetime
from langchain_core.messages import HumanMessage, SystemMessage
from services.llm_factory import llm_factory
from services.agent_manager import agent_manager
from tools.bank_account_tool import create_bank_account

class AgentPipeline:
    """Pipeline that processes chat based on agent configuration"""
    
    def __init__(self):
        print("🔧 Initializing Agent Pipeline...")
        self.chat_llm = llm_factory.get_chat_llm()
        
        # Available tools mapping
        self.tools = {
            "create_bank_account": create_bank_account
        }
        
        print("✓ Agent Pipeline initialized")
    
    def process_chat_with_agent(self, agent_id, user_message):
        """Process chat message with specific agent"""
        try:
            # Load agent configuration
            agent = agent_manager.load_agent(agent_id)
            if not agent:
                return {
                    "success": False,
                    "error": f"Agent {agent_id} not found",
                    "response": "I apologize, but the requested agent is not available."
                }
            
            print(f"💬 Agent Pipeline: Processing with {agent.name} - {user_message[:100]}...")
            
            # Create messages with agent's system prompt
            messages = []
            if agent.system_prompt:
                messages.append(SystemMessage(content=agent.system_prompt))
            messages.append(HumanMessage(content=user_message))
            
            # Get LLM response
            response = self.chat_llm.invoke(messages)
            
            # Check if agent has tools and if we should use them
            tool_result = None
            if agent.tools:
                tool_result = self._check_and_use_tools(agent, user_message, response.content)
            
            final_response = tool_result if tool_result else response.content
            
            print("✓ Agent chat processed successfully")
            
            return {
                "success": True,
                "response": final_response,
                "agent_name": agent.name
            }
            
        except Exception as e:
            error_msg = f"Agent chat error: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "response": f"I apologize, but I encountered an error: {str(e)}"
            }
    
    def _check_and_use_tools(self, agent, user_message, llm_response):
        """Check if we should use any of the agent's tools"""
        
        # Check for bank account tool
        if "create_bank_account" in agent.tools:
            if self._should_use_bank_account_tool(user_message, llm_response, agent.system_prompt):
                return self._handle_bank_account_creation(user_message)
        
        # Add more tool checks here as needed
        
        return None
    
    def _should_use_bank_account_tool(self, user_message, llm_response, system_prompt):
        """Determine if we should use the bank account creation tool"""
        
        # Check if the agent is configured for banking (look at system prompt)
        system_text = system_prompt.lower()
        is_banking_agent = any(keyword in system_text for keyword in [
            'bank', 'account', 'banking', 'financial'
        ])
        
        if not is_banking_agent:
            return False
        
        # Check if user message contains account creation intent
        combined_text = (user_message + " " + llm_response).lower()
        
        # Look for explicit account creation keywords
        account_keywords = [
            'create account', 'open account', 'new account', 
            'bank account', 'account creation', 'make account'
        ]
        
        has_account_intent = any(keyword in combined_text for keyword in account_keywords)
        
        # Check if message looks like complete account creation data (name + surname + ID)
        # Only trigger tool if we have ALL required information
        parts = user_message.strip().split()
        has_complete_data = (
            len(parts) >= 3 and 
            sum(1 for p in parts if p.isalpha()) >= 2 and
            any(p.isdigit() and len(p) >= 6 for p in parts)
        )
        
        # Only use tool if we have complete data, not just intent
        # This allows the agent to ask step by step as configured in system prompt
        return has_complete_data
    
    def _handle_bank_account_creation(self, user_message):
        """Extract info and create bank account"""
        try:
            # Clean and split the message
            parts = user_message.strip().split()
            
            print(f"🔍 Analyzing message parts: {parts}")
            
            if len(parts) >= 3:
                potential_name = None
                potential_surname = None
                potential_id = None
                
                # Find first two alphabetic words as name and surname
                alpha_words = [p for p in parts if p.isalpha()]
                if len(alpha_words) >= 2:
                    potential_name = alpha_words[0]
                    potential_surname = alpha_words[1]
                
                # Find ID (number with 6+ digits)
                for part in parts:
                    if part.isdigit() and len(part) >= 6:
                        potential_id = part
                        break
                
                print(f"🔍 Extracted: name={potential_name}, surname={potential_surname}, id={potential_id}")
                
                if potential_name and potential_surname and potential_id:
                    result = create_bank_account.invoke({
                        "name": potential_name,
                        "second_name": potential_surname, 
                        "id_number": potential_id
                    })
                    print(f"✅ Account creation result: {result}")
                    return result
            
            # If we can't extract info, ask for it
            return "I'd be happy to help you create a bank account! Please provide your information in this format: 'FirstName LastName IDNumber' (e.g., 'John Smith 123456789')"
            
        except Exception as e:
            error_msg = f"I encountered an error while creating your account: {str(e)}"
            print(f"❌ Account creation error: {error_msg}")
            return error_msg

# Global agent pipeline instance
agent_pipeline = AgentPipeline()