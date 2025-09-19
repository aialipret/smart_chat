from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from langchain_core.messages import AIMessage
from typing import TypedDict, List
from langchain_core.messages import BaseMessage
from services.llm_factory import llm_factory
from tools.bank_account_tool import create_bank_account
from .base_step import BaseStep

class LangGraphAgentStep(BaseStep):
    """Step to process chat through LangGraph agent with tools"""
    
    def __init__(self):
        super().__init__()
        
        # Get LLM and tools
        self.llm = llm_factory.get_chat_llm()
        self.tools = [create_bank_account]
        
        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # Setup LangGraph agent
        self.setup_agent()
    
    def setup_agent(self):
        """Setup LangGraph agent with ToolsNode and tools_condition"""
        
        # Define state for LangGraph
        class ChatState(TypedDict):
            messages: List[BaseMessage]
        
        # Create LangGraph workflow
        workflow = StateGraph(ChatState)
        
        # Add nodes
        workflow.add_node("llm", self._llm_node)
        workflow.add_node("tools", ToolNode(self.tools))
        
        # Set entry point
        workflow.set_entry_point("llm")
        
        # Add conditional edges using tools_condition
        workflow.add_conditional_edges(
            "llm",
            tools_condition,
            {
                "tools": "tools",
                END: END
            }
        )
        
        # Add edge from tools back to LLM
        workflow.add_edge("tools", "llm")
        
        # Compile the graph
        self.agent_graph = workflow.compile()
    
    def _llm_node(self, state):
        """LLM node for the LangGraph agent"""
        messages = state["messages"]
        
        # Debug: Log the messages being sent
        print(f"[DEBUG] LLM Node - Number of messages: {len(messages)}")
        for i, msg in enumerate(messages):
            print(f"[DEBUG] Message {i}: Type={type(msg)}, Content={getattr(msg, 'content', 'NO_CONTENT')[:100]}...")
        
        # Validate messages
        if not messages:
            raise ValueError("No messages provided to LLM")
        
        # Check if all messages have content
        for msg in messages:
            if not hasattr(msg, 'content') or not msg.content:
                raise ValueError(f"Message missing content: {msg}")
        
        response = self.llm_with_tools.invoke(messages)
        return {"messages": messages + [response]}
    
    def execute(self, context):
        """Execute LangGraph agent processing"""
        self.validate_input(context, ['prepared_messages'])
        
        self.log_step("Processing through LangGraph agent")
        
        try:
            messages = context['prepared_messages']
            
            # Debug: Log initial messages
            self.log_step(f"Starting with {len(messages)} messages")
            
            # Validate messages before processing
            for i, msg in enumerate(messages):
                if not hasattr(msg, 'content') or not msg.content:
                    raise ValueError(f"Message {i} has no content: {msg}")
            
            # Run the LangGraph agent
            result = self.agent_graph.invoke({"messages": messages})
            
            # Extract the final response
            result_messages = result["messages"]
            last_message = result_messages[-1]
            
            self.log_step(f"Agent completed with {len(result_messages)} messages")
            
            if hasattr(last_message, 'content') and last_message.content:
                response_content = last_message.content
            else:
                response_content = "I processed your request but couldn't generate a proper response."
            
            # Store results
            context['agent_response'] = response_content
            context['full_conversation'] = result_messages
            context['success'] = True
            
            self.log_step("LangGraph agent processing completed")
            
        except Exception as e:
            error_msg = f"LangGraph agent error: {str(e)}"
            self.log_step(error_msg)
            
            # Fallback response
            context['agent_response'] = f"I apologize, but I encountered an error: {str(e)}"
            context['success'] = False
            context['error'] = error_msg
        
        return context