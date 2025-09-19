"""
Agent Manager - Handles multiple AI agents with their own configurations
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from services.llm_factory import llm_factory

@dataclass
class AgentConfig:
    """Configuration for an AI agent"""
    id: str
    name: str
    description: str
    system_prompt: str
    tools: List[str]
    flows: List[str]
    created_at: str
    updated_at: str
    active: bool = True

class AgentManager:
    """Manages multiple AI agents and their configurations"""
    
    def __init__(self):
        self.agents_dir = 'agents'
        self.flows_dir = 'flows'
        self.tools_dir = 'tools'
        
        # Ensure directories exist
        os.makedirs(self.agents_dir, exist_ok=True)
        os.makedirs(self.flows_dir, exist_ok=True)
        os.makedirs(self.tools_dir, exist_ok=True)
        
        # Initialize with default agents if none exist
        self._initialize_default_agents()
    
    def _initialize_default_agents(self):
        """Create default agents if none exist"""
        if not self.list_agents():
            # Banking Assistant
            banking_agent = AgentConfig(
                id="banking_assistant",
                name="Banking Assistant",
                description="Specialized in bank account creation and banking services",
                system_prompt="""You are a helpful banking assistant that specializes in creating bank accounts. 

When users provide their information (first name, last name, and ID number), you should help them create a bank account. 

If they provide information like "John Smith 123456789", recognize this as a bank account creation request.

Be friendly and helpful, and guide users through the account creation process.""",
                tools=["create_bank_account"],
                flows=["bank_account_creation"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Customer Support Agent
            support_agent = AgentConfig(
                id="customer_support",
                name="Customer Support",
                description="General customer support and inquiry handling",
                system_prompt="""You are a helpful customer support assistant. You can help with:
- General inquiries
- Product information
- Troubleshooting
- Account questions

Be professional, empathetic, and solution-oriented in your responses.""",
                tools=[],
                flows=["customer_support_flow"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Sales Assistant
            sales_agent = AgentConfig(
                id="sales_assistant",
                name="Sales Assistant",
                description="Product recommendations and sales support",
                system_prompt="""You are a knowledgeable sales assistant. You help customers:
- Discover products that meet their needs
- Understand product features and benefits
- Make informed purchasing decisions
- Process orders and handle sales inquiries

Be consultative, informative, and customer-focused.""",
                tools=[],
                flows=["sales_flow"],
                created_at=datetime.now().isoformat(),
                updated_at=datetime.now().isoformat()
            )
            
            # Save default agents
            self.save_agent(banking_agent)
            self.save_agent(support_agent)
            self.save_agent(sales_agent)
    
    def list_agents(self) -> List[Dict]:
        """List all available agents"""
        agents = []
        if os.path.exists(self.agents_dir):
            for filename in os.listdir(self.agents_dir):
                if filename.endswith('.json'):
                    try:
                        agent = self.load_agent(filename[:-5])  # Remove .json
                        if agent:
                            agents.append(asdict(agent))
                    except Exception as e:
                        print(f"Error loading agent {filename}: {e}")
        return agents
    
    def load_agent(self, agent_id: str) -> Optional[AgentConfig]:
        """Load a specific agent by ID"""
        filepath = os.path.join(self.agents_dir, f"{agent_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r') as f:
                    data = json.load(f)
                    return AgentConfig(**data)
            except Exception as e:
                print(f"Error loading agent {agent_id}: {e}")
        return None
    
    def save_agent(self, agent: AgentConfig) -> bool:
        """Save an agent configuration"""
        try:
            filepath = os.path.join(self.agents_dir, f"{agent.id}.json")
            agent.updated_at = datetime.now().isoformat()
            
            with open(filepath, 'w') as f:
                json.dump(asdict(agent), f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving agent {agent.id}: {e}")
            return False
    
    def create_agent(self, name: str, description: str, system_prompt: str, 
                    tools: List[str] = None, flows: List[str] = None) -> AgentConfig:
        """Create a new agent"""
        agent_id = name.lower().replace(' ', '_').replace('-', '_')
        
        agent = AgentConfig(
            id=agent_id,
            name=name,
            description=description,
            system_prompt=system_prompt,
            tools=tools or [],
            flows=flows or [],
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat()
        )
        
        self.save_agent(agent)
        return agent
    
    def update_agent(self, agent_id: str, **kwargs) -> bool:
        """Update an existing agent"""
        agent = self.load_agent(agent_id)
        if not agent:
            return False
        
        # Update fields
        for key, value in kwargs.items():
            if hasattr(agent, key):
                setattr(agent, key, value)
        
        return self.save_agent(agent)
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        filepath = os.path.join(self.agents_dir, f"{agent_id}.json")
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
                return True
            except Exception as e:
                print(f"Error deleting agent {agent_id}: {e}")
        return False
    
    def get_agent_flows(self, agent_id: str) -> List[Dict]:
        """Get flows associated with an agent"""
        agent = self.load_agent(agent_id)
        if not agent:
            return []
        
        flows = []
        for flow_name in agent.flows:
            flow_path = os.path.join(self.flows_dir, f"{flow_name}.json")
            if os.path.exists(flow_path):
                try:
                    with open(flow_path, 'r') as f:
                        flow_data = json.load(f)
                        flows.append(flow_data)
                except Exception as e:
                    print(f"Error loading flow {flow_name}: {e}")
        
        return flows
    
    def assign_flow_to_agent(self, agent_id: str, flow_name: str) -> bool:
        """Assign a flow to an agent"""
        agent = self.load_agent(agent_id)
        if not agent:
            return False
        
        if flow_name not in agent.flows:
            agent.flows.append(flow_name)
            return self.save_agent(agent)
        
        return True
    
    def remove_flow_from_agent(self, agent_id: str, flow_name: str) -> bool:
        """Remove a flow from an agent"""
        agent = self.load_agent(agent_id)
        if not agent:
            return False
        
        if flow_name in agent.flows:
            agent.flows.remove(flow_name)
            return self.save_agent(agent)
        
        return True
    
    def get_available_tools(self) -> List[str]:
        """Get list of available tools"""
        tools = []
        if os.path.exists(self.tools_dir):
            for filename in os.listdir(self.tools_dir):
                if filename.endswith('_tool.py'):
                    tool_name = filename[:-8]  # Remove _tool.py
                    tools.append(tool_name)
        return tools
    
    def get_available_flows(self) -> List[Dict]:
        """Get list of available flows"""
        flows = []
        if os.path.exists(self.flows_dir):
            for filename in os.listdir(self.flows_dir):
                if filename.endswith('.json'):
                    try:
                        with open(os.path.join(self.flows_dir, filename), 'r') as f:
                            flow_data = json.load(f)
                            flows.append({
                                'filename': filename,
                                'id': filename[:-5],  # Remove .json extension
                                'name': flow_data.get('workflow_name', filename[:-5]),
                                'description': flow_data.get('description', ''),
                                'created_at': flow_data.get('created_at', '')
                            })
                    except Exception as e:
                        print(f"Error reading flow {filename}: {e}")
        return flows
    
    def get_flow_by_id(self, flow_id: str) -> Optional[Dict]:
        """Get a specific flow by ID"""
        flow_path = os.path.join(self.flows_dir, f"{flow_id}.json")
        if os.path.exists(flow_path):
            try:
                with open(flow_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading flow {flow_id}: {e}")
        return None

# Global agent manager instance
agent_manager = AgentManager()