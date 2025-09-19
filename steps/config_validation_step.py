import json
import os
from datetime import datetime
from .base_step import BaseStep

class ConfigValidationStep(BaseStep):
    """Step to validate and save workflow configuration JSON"""
    
    def __init__(self):
        super().__init__()
        self.flows_folder = 'flows'
        
        # Ensure flows directory exists
        os.makedirs(self.flows_folder, exist_ok=True)
    
    def execute(self, context):
        """Validate JSON and save to flows folder"""
        self.validate_input(context, ['raw_config'])
        
        self.log_step("Validating and saving config")
        
        try:
            # Parse JSON
            config_data = json.loads(context['raw_config'])
            
            # Add timestamp if not present
            if "created_at" not in config_data:
                config_data["created_at"] = datetime.now().isoformat()
            
            # Validate required fields
            required_fields = ["workflow_name", "description", "steps", "system_instructions"]
            for field in required_fields:
                if field not in config_data:
                    raise ValueError(f"Missing required field: {field}")
            
            # Generate filename
            workflow_name = config_data["workflow_name"].lower().replace(" ", "_")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{workflow_name}_{timestamp}.json"
            filepath = os.path.join(self.flows_folder, filename)
            
            # Save to flows folder
            with open(filepath, 'w') as f:
                json.dump(config_data, f, indent=2)
            
            self.log_step(f"Config saved to: {filepath}")
            
            # Store results in context
            context['validated_config'] = config_data
            context['config_filepath'] = filepath
            context['config_filename'] = filename
            context['success'] = True
            context['message'] = f"Workflow configuration saved successfully to {filename}"
            
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON format: {str(e)}"
            self.log_step(f"JSON Error: {error_msg}")
            self.log_step(f"Raw config that failed to parse: {repr(context['raw_config'])}")
            context['success'] = False
            context['error'] = error_msg
            context['raw_output'] = context['raw_config']
            
        except Exception as e:
            error_msg = f"Validation error: {str(e)}"
            self.log_step(f"Validation Error: {error_msg}")
            context['success'] = False
            context['error'] = error_msg
        
        return context