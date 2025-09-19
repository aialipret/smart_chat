# Flow Configuration & Chat Application

A Flask-based application that combines workflow configuration with AI-powered chat functionality using LangChain and LangGraph.

## Features

### Config Tab
- **Flow Generation**: Describe your workflow in natural language
- **LangChain Steps**: Uses sequential steps to process and generate flow configurations
- **JSON Output**: Converts workflow descriptions to structured JSON configurations
- **Local Storage**: Saves configurations to local files for persistence

### Chat Tab
- **LangGraph Agent**: AI agent with tool integration
- **System Prompt Integration**: Uses saved flow configurations as system prompts
- **Tool Support**: Bank account creation tool with validation
- **Interactive UI**: Real-time chat interface

## Architecture

```
├── app.py                          # Main Flask application with separate APIs
├── services/                       # Core services
│   ├── llm_factory.py             # Singleton LLM factory for efficient reuse
│   └── pipeline_manager.py        # Coordinates config and chat pipelines
├── pipelines/                      # Two separate pipelines
│   ├── config_pipeline.py         # Config generation pipeline
│   └── chat_pipeline.py           # Chat processing pipeline
├── steps/                          # All processing steps (shared)
│   ├── base_step.py               # Base step class
│   ├── config_generation_step.py  # LLM-based config generation
│   ├── config_validation_step.py  # JSON validation and saving
│   ├── chat_preparation_step.py   # Chat input preparation
│   ├── langgraph_agent_step.py    # LangGraph agent with ToolsNode
│   └── response_extraction_step.py # Response formatting
├── config/                         # Flow configuration module (legacy support)
│   └── flow_manager.py            # Manages flow storage and loading
├── chat/                          # Chat agent module (legacy support)
│   ├── agent_manager.py           # Agent management
│   ├── state.py                   # Agent state definition
│   ├── nodes/                     # LangGraph nodes
│   │   └── llm_node.py           # LLM processing node
│   └── tools/                     # Available tools
│       └── bank_account_tool.py   # Bank account creation with validation
├── templates/                     # HTML templates
│   └── index.html                # Main UI template
├── static/js/                     # Frontend JavaScript
│   └── app.js                    # Main application logic
├── flows/                         # Generated workflow configurations
│   └── *.json                    # Individual workflow files
└── data/                          # Local data storage
    └── flow_config.json          # Legacy flow configurations
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   # Edit .env and add your Google API key for Gemini
   ```

3. **Run Application**
   ```bash
   python app.py
   ```

4. **Access Application**
   Open http://localhost:5000 in your browser

## Usage

### Creating Flow Configurations

1. Go to the **Config** tab
2. Describe your desired workflow in the text area
3. Click **Generate Flow** to create a JSON configuration
4. Review the generated configuration
5. Click **Save Flow** to store it locally

### Using the Chat Agent

1. Go to the **Chat** tab
2. The agent will use your saved flow configuration as context
3. Type messages to interact with the AI agent
4. The agent can use tools like calculator and web search

## Extending the Application

### Adding New Steps
Create new step classes in `config/steps/` that inherit from `BaseStep`:

```python
from .base_step import BaseStep

class CustomStep(BaseStep):
    def execute(self, context):
        # Your step logic here
        return context
```

### Adding New Tools
Create new tools using LangChain's `@tool` decorator in `chat/tools/`:

```python
from langchain.tools import tool

@tool
def custom_tool(param1: str, param2: int) -> str:
    """
    Description of what this tool does.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2
        
    Returns:
        str: Description of return value
    """
    # Your tool logic here
    return "Tool result"
```

Then add it to the agent manager's tools list and bind it to the LLM.

## API Endpoints

### Legacy Endpoints (use managers)
- `POST /api/config/generate-flow` - Generate flow configuration
- `POST /api/config/save-flow` - Save flow configuration  
- `GET /api/config/load-flow` - Load existing flow configuration
- `GET /api/config/list-flows` - List all saved flows
- `GET /api/config/load-flow/<filename>` - Load specific flow
- `POST /api/chat/message` - Process chat messages

### Direct Pipeline Endpoints
- `POST /api/pipelines/config` - Direct Config Pipeline API
- `POST /api/pipelines/chat` - Direct Chat Pipeline API

## Dependencies

- **Flask**: Web framework
- **LangChain**: LLM integration and chains
- **LangGraph**: Agent workflow management
- **Google Gemini**: LLM provider (Gemini 1.5 Flash)
- **Bootstrap**: Frontend UI framework

## Benefits of Gemini Flash 1.5:
- **Faster responses** than GPT models
- **Lower cost** for API calls
- **Better JSON generation** capabilities
- **Larger context window** for complex workflows

## Key Architecture Features:

### **Two Separate Pipelines**

#### **Config Pipeline (`pipelines/config_pipeline.py`)**
- **Steps**: Config Generation → Config Validation → Save to flows/
- **Processing**: Text → LLM → JSON → Validation → File Save
- **Pipeline**: Uses `|` operator to chain steps
- **Output**: Saves to `flows/` folder with timestamp

#### **Chat Pipeline (`pipelines/chat_pipeline.py`)**
- **Steps**: Chat Preparation → LangGraph Agent → Response Extraction
- **LangGraph Integration**: Uses ToolsNode and tools_condition
- **Tool Binding**: Bank account tool properly bound to LLM
- **Pipeline**: Uses `|` operator to chain steps

### **Unified Steps Folder (`steps/`)**
- **Shared Steps**: All processing steps in one location
- **Base Step**: Common interface for all steps
- **Modular Design**: Steps can be reused across pipelines
- **Clean Separation**: Config and chat steps clearly defined

### **LLM Factory Pattern**
- **Singleton Design**: Single LLM factory instance across the application
- **Instance Caching**: Reuses LLM instances with same parameters
- **Specialized LLMs**: Different configurations for config generation vs chat
- **Memory Efficient**: Avoids multiple LLM initializations

### **Pipeline Architecture**
- **Separate Flows**: Clean separation between config generation and chat
- **LangChain Pipelines**: Uses `|` operator for pipeline composition
- **LangGraph Integration**: Proper use of ToolsNode and tools_condition
- **Error Handling**: Robust error handling and fallback mechanisms

The architecture follows the same pattern as arch_asistant - centralized LLM management with pipeline-based processing, powered by Google's Gemini Flash 1.5!