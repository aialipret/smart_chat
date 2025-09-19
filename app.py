from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from pipeline import pipeline
from services.agent_manager import agent_manager
from services.agent_pipeline import agent_pipeline

# Load environment variables
load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/config/generate-flow', methods=['POST'])
def generate_flow():
    """Config API - Generate workflow configuration"""
    try:
        data = request.json
        user_input = data.get('input', '')
        
        result = pipeline.process_config(user_input)
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unknown error'),
                'raw_output': result.get('raw_output', '')
            }), 400
        
        return jsonify({
            'success': True,
            'flow_config': result['config'],
            'filepath': result.get('filepath'),
            'filename': result.get('filename'),
            'message': result.get('message')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/save-flow', methods=['POST'])
def save_flow():
    try:
        data = request.json
        flow_config = data.get('flow_config')
        
        pipeline.save_flow_config(flow_config)
        
        return jsonify({
            'success': True,
            'message': 'Flow configuration saved successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/message', methods=['POST'])
def chat_message():
    """Chat API - Process chat message"""
    try:
        data = request.json
        user_message = data.get('message', '')
        system_prompt = data.get('system_prompt')
        
        # If no system prompt provided, try to load from flow config
        if not system_prompt:
            system_prompt = pipeline.load_system_prompt()
        
        result = pipeline.process_chat(user_message, system_prompt)
        
        return jsonify({
            'success': result.get('success', True),
            'response': result.get('response', 'No response generated'),
            'error': result.get('error')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f"I apologize, but I encountered an error: {str(e)}"
        }), 500

@app.route('/api/config/load-flow', methods=['GET'])
def load_flow():
    try:
        flow_config = pipeline.load_flow_config()
        return jsonify({
            'success': True,
            'flow_config': flow_config
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/list-flows', methods=['GET'])
def list_flows():
    try:
        flows = pipeline.list_saved_flows()
        return jsonify({
            'success': True,
            'flows': flows
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/config/load-flow/<filename>', methods=['GET'])
def load_flow_by_name(filename):
    try:
        flow_config = pipeline.load_flow_by_filename(filename)
        if flow_config:
            return jsonify({
                'success': True,
                'flow_config': flow_config
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Flow not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Dedicated Pipeline API Endpoints

@app.route('/api/pipelines/config', methods=['POST'])
def config_pipeline_api():
    """Direct Config Pipeline API"""
    try:
        data = request.json
        user_input = data.get('input', '')
        
        result = pipeline.process_config(user_input)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Config pipeline error: {str(e)}"
        }), 500

@app.route('/api/pipelines/chat', methods=['POST'])
def chat_pipeline_api():
    """Direct Chat Pipeline API"""
    try:
        data = request.json
        user_message = data.get('message', '')
        system_prompt = data.get('system_prompt', 'You are a helpful assistant that can create bank accounts.')
        
        result = pipeline.process_chat(user_message, system_prompt)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f"Chat pipeline error: {str(e)}",
            'response': f"Pipeline error: {str(e)}"
        }), 500

# Agent Management API Endpoints

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """Get list of all agents"""
    try:
        agents = agent_manager.list_agents()
        return jsonify({
            'success': True,
            'agents': agents
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    """Get specific agent details"""
    try:
        agent = agent_manager.load_agent(agent_id)
        if agent:
            return jsonify({
                'success': True,
                'agent': agent.__dict__
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Agent not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents', methods=['POST'])
def create_agent():
    """Create a new agent"""
    try:
        data = request.json
        name = data.get('name')
        description = data.get('description', '')
        system_prompt = data.get('system_prompt', '')
        tools = data.get('tools', [])
        flows = data.get('flows', [])
        
        if not name:
            return jsonify({
                'success': False,
                'error': 'Agent name is required'
            }), 400
        
        agent = agent_manager.create_agent(name, description, system_prompt, tools, flows)
        
        return jsonify({
            'success': True,
            'agent': agent.__dict__,
            'message': f'Agent "{name}" created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/<agent_id>', methods=['PUT'])
def update_agent(agent_id):
    """Update an existing agent"""
    try:
        data = request.json
        success = agent_manager.update_agent(agent_id, **data)
        
        if success:
            agent = agent_manager.load_agent(agent_id)
            return jsonify({
                'success': True,
                'agent': agent.__dict__,
                'message': 'Agent updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Agent not found or update failed'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id):
    """Delete an agent"""
    try:
        success = agent_manager.delete_agent(agent_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Agent deleted successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Agent not found or deletion failed'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/<agent_id>/flows', methods=['GET'])
def get_agent_flows(agent_id):
    """Get flows for a specific agent"""
    try:
        flows = agent_manager.get_agent_flows(agent_id)
        return jsonify({
            'success': True,
            'flows': flows
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/<agent_id>/flows/<flow_name>', methods=['POST'])
def assign_flow_to_agent(agent_id, flow_name):
    """Assign a flow to an agent"""
    try:
        success = agent_manager.assign_flow_to_agent(agent_id, flow_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Flow "{flow_name}" assigned to agent'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Assignment failed'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/<agent_id>/flows/<flow_name>', methods=['DELETE'])
def remove_flow_from_agent(agent_id, flow_name):
    """Remove a flow from an agent"""
    try:
        success = agent_manager.remove_flow_from_agent(agent_id, flow_name)
        
        if success:
            return jsonify({
                'success': True,
                'message': f'Flow "{flow_name}" removed from agent'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Removal failed'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/tools', methods=['GET'])
def get_available_tools():
    """Get list of available tools"""
    try:
        tools = agent_manager.get_available_tools()
        return jsonify({
            'success': True,
            'tools': tools
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/flows', methods=['GET'])
def get_available_flows():
    """Get list of available flows"""
    try:
        flows = agent_manager.get_available_flows()
        return jsonify({
            'success': True,
            'flows': flows
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/flows/<flow_id>', methods=['GET'])
def get_flow_details(flow_id):
    """Get details of a specific flow"""
    try:
        flow = agent_manager.get_flow_by_id(flow_id)
        if flow:
            return jsonify({
                'success': True,
                'flow': flow
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Flow not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/agents/<agent_id>/system-prompt', methods=['PUT'])
def update_agent_system_prompt(agent_id):
    """Update agent's system prompt"""
    try:
        data = request.json
        system_prompt = data.get('system_prompt', '')
        
        if not system_prompt.strip():
            return jsonify({
                'success': False,
                'error': 'System prompt cannot be empty'
            }), 400
        
        success = agent_manager.update_agent(agent_id, system_prompt=system_prompt)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'System prompt updated successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Agent not found or update failed'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/chat/agent/<agent_id>', methods=['POST'])
def chat_with_agent(agent_id):
    """Chat with a specific agent"""
    try:
        data = request.json
        user_message = data.get('message', '')
        
        # Use the new agent-aware pipeline
        result = agent_pipeline.process_chat_with_agent(agent_id, user_message)
        
        return jsonify(result)
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'response': f"I apologize, but I encountered an error: {str(e)}"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)