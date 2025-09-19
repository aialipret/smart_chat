"""
Single Pipeline Manager - Handles both config and chat processing
"""

import os
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from services.llm_factory import llm_factory
from tools.bank_account_tool import create_bank_account
import re

load_dotenv()

class Pipeline:
    """Single pipeline for both config and chat processing"""
    
    def __init__(self):
        print("🔧 Initializing Pipeline...")
        
        # Get LLMs from factory
        self.config_llm = llm_factory.get_config_llm()
        self.chat_llm = llm_factory.get_chat_llm()
        
        # Tools
        self.tools = {"create_bank_account": create_bank_account}
        
        # Ensure directories exist
        os.makedirs('flows', exist_ok=True)
        os.makedirs('data', exist_ok=True)
        
        # Setup pipelines
        self.setup_pipelines()
        print("✓ Pipeline initialized")
    
    def setup_pipelines(self):
        """Setup both config and chat pipelines"""
        
        # Config pipeline
        self.config_pipeline = (
            RunnableLambda(self._prepare_config_input)
            | RunnableLambda(self._generate_config)
            | RunnableLambda(self._validate_and_save_config)
        )
        
        # Chat pipeline
        self.chat_pipeline = (
            RunnableLambda(self._prepare_chat_input)
            | RunnableLambda(self._process_chat)
            | RunnableLambda(self._format_chat_response)
        )
    
    # Config Pipeline Methods
    def _prepare_config_input(self, user_input):
        """Prepare input for config generation"""
        if isinstance(user_input, dict):
            input_text = user_input.get('input', '')
        else:
            input_text = str(user_input)
        
        print(f"📝 Config Pipeline: Processing - {input_text[:100]}...")
        return {"user_input": input_text}
    
    def _generate_config(self, context):
        """Generate workflow configuration using LLM"""
        
        json_format = {
            "workflow_name": "string - descriptive name",
            "description": "string - brief description", 
            "version": "string - version number",
            "created_at": "string - ISO timestamp",
            "steps": [
                {
                    "step_id": "string - unique identifier",
                    "name": "string - step name",
                    "description": "string - what this step does",
                    "type": "string - step type",
                    "parameters": "object - parameters",
                    "next_step": "string - next step ID or null"
                }
            ],
            "flow_logic": "string - how steps connect",
            "system_instructions": "string - AI behavior instructions",
            "triggers": ["array - what triggers this workflow"],
            "expected_outputs": ["array - expected outputs"]
        }
        
        prompt = ChatPromptTemplate.from_template("""
        You are an AI workflow designer. Create a structured workflow configuration in JSON format.

        User Input: {user_input}

        Create a JSON configuration that follows this EXACT format:
        {json_format}

        Requirements:
        1. Use exact field names and structure
        2. Fill realistic values based on user description
        3. Create 2-5 logical steps
        4. Ensure proper step flow with next_step references
        5. Make system_instructions detailed and actionable
        6. Include relevant triggers and outputs

        Respond ONLY with valid JSON, no markdown, no explanation.
        Start with {{ and end with }}.
        """)
        
        try:
            result = (prompt | self.config_llm | StrOutputParser()).invoke({
                "user_input": context['user_input'],
                "json_format": json.dumps(json_format, indent=2)
            })
            
            # Clean markdown if present
            cleaned = self._clean_json_response(result)
            context['raw_config'] = cleaned
            
            print(f"✓ Config generated: {len(cleaned)} characters")
            
        except Exception as e:
            print(f"❌ Config generation error: {e}")
            context['error'] = str(e)
        
        return context
    
    def _validate_and_save_config(self, context):
        """Validate and save configuration"""
        if 'error' in context:
            return {
                "success": False,
                "error": context['error']
            }
        
        try:
            # Parse JSON
            config_data = json.loads(context['raw_config'])
            
            # Add timestamp
            if "created_at" not in config_data:
                config_data["created_at"] = datetime.now().isoformat()
            
            # Validate required fields
            required = ["workflow_name", "description", "steps", "system_instructions"]
            for field in required:
                if field not in config_data:
                    raise ValueError(f"Missing field: {field}")
            
            # Generate filename and save
            name = config_data["workflow_name"].lower().replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{name}_{timestamp}.json"
            filepath = os.path.join('flows', filename)
            
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            print(f"✅ Config saved: {filepath}")
            
            return {
                "success": True,
                "config": config_data,
                "filepath": filepath,
                "filename": filename,
                "message": f"Configuration saved to {filename}"
            }
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON: {str(e)}"
            print(f"❌ JSON Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "raw_output": context.get('raw_config', '')
            }
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            print(f"❌ Validation Error: {error_msg}")
            return {
                "success": False,
                "error": error_msg,
                "raw_output": context.get('raw_config', '')
            }
    
    def _clean_json_response(self, response):
        """Clean JSON response by removing markdown"""
        if not response:
            return ""
        
        cleaned = response.strip()
        
        # Remove markdown code blocks
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]
        
        return cleaned.strip()
    
    # Chat Pipeline Methods
    def _prepare_chat_input(self, inputs):
        """Prepare chat input"""
        user_message = inputs.get("message", "")
        system_prompt = inputs.get("system_prompt", """You are a helpful banking assistant that specializes in creating bank accounts. 

When users provide their information (first name, last name, and ID number), you should help them create a bank account. 

If they provide information like "John Smith 123456789", recognize this as a bank account creation request.

Be friendly and helpful, and guide users through the account creation process.""")
        
        print(f"💬 Chat Pipeline: Processing - {user_message[:100]}...")
        
        return {
            "user_message": user_message,
            "system_prompt": system_prompt
        }
    
    def _process_chat(self, context):
        """Process chat with LLM and tools"""
        try:
            user_message = context['user_message']
            system_prompt = context['system_prompt']
            
            # Create messages
            messages = []
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            messages.append(HumanMessage(content=user_message))
            
            # Get LLM response
            response = self.chat_llm.invoke(messages)
            
            # Check if we should use bank account tool
            if self._should_create_account(user_message, response.content):
                tool_result = self._handle_bank_account_creation(user_message)
                if tool_result:
                    context['response'] = tool_result
                else:
                    context['response'] = response.content
            else:
                context['response'] = response.content
            
            context['success'] = True
            print("✓ Chat processed successfully")
            
        except Exception as e:
            error_msg = f"Chat error: {str(e)}"
            print(f"❌ {error_msg}")
            context['response'] = f"I apologize, but I encountered an error: {str(e)}"
            context['success'] = False
            context['error'] = error_msg
        
        return context
    
    def _format_chat_response(self, context):
        """Format final chat response"""
        return {
            "success": context.get('success', True),
            "response": context.get('response', 'No response generated'),
            "error": context.get('error')
        }
    
    def _should_create_account(self, user_message, response_content):
        """Check if we should create a bank account"""
        keywords = ['bank account', 'create account', 'open account', 'account creation', 'account', 'banking']
        text = (user_message + " " + response_content).lower()
        
        # Check for keywords OR if message looks like account info (name name number)
        has_keywords = any(keyword in text for keyword in keywords)
        
        # Check if message looks like account creation data (2+ words + number)
        parts = user_message.strip().split()
        has_account_pattern = (len(parts) >= 3 and 
                              sum(1 for p in parts if p.isalpha()) >= 2 and
                              any(p.isdigit() and len(p) >= 6 for p in parts))
        
        return has_keywords or has_account_pattern
    
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
    
    # Public Methods
    def process_config(self, user_input):
        """Process config generation"""
        return self.config_pipeline.invoke(user_input)
    
    def process_chat(self, user_message, system_prompt=None):
        """Process chat message"""
        return self.chat_pipeline.invoke({
            "message": user_message,
            "system_prompt": system_prompt
        })
    
    # Legacy support methods
    def load_flow_config(self):
        """Load legacy flow config"""
        legacy_path = 'data/flow_config.json'
        if os.path.exists(legacy_path):
            with open(legacy_path, 'r') as f:
                data = json.load(f)
                return data.get('flow_config')
        return None
    
    def save_flow_config(self, flow_config):
        """Save legacy flow config"""
        legacy_path = 'data/flow_config.json'
        config_data = {
            'flow_config': flow_config,
            'created_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        with open(legacy_path, 'w') as f:
            json.dump(config_data, f, indent=2)
    
    def load_system_prompt(self):
        """Load system prompt from flow config"""
        flow_config = self.load_flow_config()
        if flow_config and isinstance(flow_config, dict):
            return flow_config.get('system_instructions', 'You are a helpful banking assistant.')
        
        return """You are a helpful banking assistant that specializes in creating bank accounts. 

When users provide their information (first name, last name, and ID number), you should help them create a bank account. 

If they provide information like "John Smith 123456789", recognize this as a bank account creation request.

Be friendly and helpful, and guide users through the account creation process."""
    
    def list_saved_flows(self):
        """List all saved flows"""
        flows = []
        if os.path.exists('flows'):
            for filename in os.listdir('flows'):
                if filename.endswith('.json'):
                    filepath = os.path.join('flows', filename)
                    try:
                        with open(filepath, 'r') as f:
                            flow_data = json.load(f)
                            flows.append({
                                'filename': filename,
                                'workflow_name': flow_data.get('workflow_name', 'Unknown'),
                                'description': flow_data.get('description', ''),
                                'created_at': flow_data.get('created_at', ''),
                                'filepath': filepath
                            })
                    except Exception as e:
                        print(f"Error reading {filename}: {e}")
        return flows
    
    def load_flow_by_filename(self, filename):
        """Load specific flow by filename"""
        filepath = os.path.join('flows', filename)
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
        return None

# Global pipeline instance
pipeline = Pipeline()