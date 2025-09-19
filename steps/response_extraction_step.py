from .base_step import BaseStep

class ResponseExtractionStep(BaseStep):
    """Step to extract and format the final response"""
    
    def execute(self, context):
        """Extract final response from agent processing"""
        self.log_step("Extracting final response")
        
        try:
            # Get the response from previous step
            if 'agent_response' in context:
                final_response = context['agent_response']
            else:
                final_response = "I apologize, but I couldn't process your request."
            
            # Store final response
            context['final_response'] = final_response
            
            self.log_step("Response extraction completed")
            
        except Exception as e:
            self.log_step(f"Error extracting response: {str(e)}")
            context['final_response'] = "I apologize, but I encountered an error processing your request."
        
        return context