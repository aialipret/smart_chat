import json
from datetime import datetime
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from services.llm_factory import llm_factory
from .base_step import BaseStep

class ConfigGenerationStep(BaseStep):
    """Step to generate workflow configuration JSON from user input"""
    
    def __init__(self):
        super().__init__()
        self.llm = llm_factory.get_config_llm()
        
        # Define the JSON format template
        self.json_format = {
            "workflow_name": "string - descriptive name for the workflow",
            "description": "string - brief description of what this workflow does", 
            "version": "string - version number (e.g., '1.0')",
            "created_at": "string - ISO timestamp",
            "steps": [
                {
                    "step_id": "string - unique identifier",
                    "name": "string - step name",
                    "description": "string - what this step does",
                    "type": "string - type of step (input, processing, output, decision, etc.)",
                    "parameters": "object - any parameters needed for this step",
                    "next_step": "string - ID of next step or null for end"
                }
            ],
            "flow_logic": "string - description of how steps connect and flow",
            "system_instructions": "string - instructions for AI behavior when following this workflow",
            "triggers": ["array of strings - what triggers this workflow"],
            "expected_outputs": ["array of strings - what outputs this workflow produces"]
        }
        
        # Setup prompt template
        self.prompt = ChatPromptTemplate.from_template("""
        You are an AI workflow designer. Create a structured workflow configuration in JSON format based on the user's description.

        User Input: {user_input}

        Create a JSON configuration that follows this EXACT format:
        {json_format}

        Requirements:
        1. Use the exact field names and structure shown above
        2. Fill in realistic values based on the user's description
        3. Create at least 2-5 logical steps for the workflow
        4. Ensure steps have proper flow with next_step references
        5. Make system_instructions detailed and actionable
        6. Include relevant triggers and expected outputs

        Respond ONLY with valid JSON, no additional text, no markdown code blocks, no explanation.
        Do NOT wrap the JSON in ```json or ``` markers.
        Start directly with {{ and end with }}.
        """)
        
        # Create pipeline
        self.pipeline = (
            self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def execute(self, context):
        """Generate workflow configuration from user input"""
        self.validate_input(context, ['user_input'])
        
        self.log_step(f"Generating config for: {context['user_input']}")
        
        try:
            # Generate config using LLM
            result = self.pipeline.invoke({
                "user_input": context['user_input'],
                "json_format": json.dumps(self.json_format, indent=2)
            })
            
            # Debug: Log the raw result
            self.log_step(f"Raw LLM result: {repr(result)}")
            
            # Clean the result - remove markdown code blocks if present
            cleaned_result = self._clean_json_response(result)
            
            # Store raw output for validation step
            context['raw_config'] = cleaned_result
            
            if not context['raw_config']:
                raise ValueError("LLM returned empty response")
            
            self.log_step("Config generation completed")
            
        except Exception as e:
            self.log_step(f"Error generating config: {str(e)}")
            raise
        
        return context
    
    def _clean_json_response(self, response):
        """Clean JSON response by removing markdown code blocks"""
        if not response:
            return ""
        
        # Remove markdown code blocks
        cleaned = response.strip()
        
        # Remove ```json and ``` markers
        if cleaned.startswith('```json'):
            cleaned = cleaned[7:]  # Remove ```json
        elif cleaned.startswith('```'):
            cleaned = cleaned[3:]   # Remove ```
        
        if cleaned.endswith('```'):
            cleaned = cleaned[:-3]  # Remove trailing ```
        
        return cleaned.strip()