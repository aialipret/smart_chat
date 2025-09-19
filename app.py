from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from pipeline import pipeline

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)