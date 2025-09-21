"""
Base Agent class that all other agents inherit from
"""

import json
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from utils.json_parser import JSONParser

logger = logging.getLogger(__name__)

class BaseAgent(ABC):
    """
    Abstract base class for all AI agents in the interview system
    """
    
    def __init__(self, name: str, llm_client, tools: Optional[list] = None):
        """
        Initialize the base agent
        
        Args:
            name (str): Name of the agent
            llm_client: The LLM client (Gemini) to use
            tools (list, optional): List of tools available to the agent
        """
        self.name = name
        self.llm_client = llm_client
        self.tools = tools or []
        self.conversation_history = []
        
    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the system prompt that defines this agent's role and behavior
        
        Returns:
            str: The system prompt for this agent
        """
        pass
    
    def add_tool(self, tool_name: str, tool_function):
        """
        Add a tool to the agent's available tools
        
        Args:
            tool_name (str): Name of the tool
            tool_function: The function to execute
        """
        self.tools.append({
            'name': tool_name,
            'function': tool_function
        })
    
    def execute_tool(self, tool_name: str, **kwargs):
        """
        Execute a specific tool by name
        
        Args:
            tool_name (str): Name of the tool to execute
            **kwargs: Arguments to pass to the tool function
            
        Returns:
            Any: Result from the tool execution
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                try:
                    return tool['function'](**kwargs)
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {str(e)}")
                    return None
        
        logger.warning(f"Tool {tool_name} not found")
        return None
    
    def _serialize_context_safely(self, context: Dict[str, Any]) -> str:
        """
        Safely serialize context, handling non-serializable objects
        
        Args:
            context: Context dictionary
            
        Returns:
            str: Serialized context string
        """
        def safe_serialize(obj):
            """Recursively serialize objects, converting non-serializable types"""
            if obj is None:
                return None
            elif isinstance(obj, (str, int, float, bool)):
                return obj
            elif isinstance(obj, (list, tuple)):
                return [safe_serialize(item) for item in obj]
            elif isinstance(obj, dict):
                return {key: safe_serialize(value) for key, value in obj.items()}
            else:
                # Convert non-serializable objects to string representation
                return str(obj)
        
        try:
            safe_context = safe_serialize(context)
            return json.dumps(safe_context, indent=2)
        except Exception as e:
            logger.warning(f"Context serialization failed: {e}, using string representation")
            return str(context)
    
    def generate_response(self, user_input: str, context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate a response using the LLM client
        
        Args:
            user_input (str): The user's input or question
            context (dict, optional): Additional context for the response
            
        Returns:
            dict: The agent's response
        """
        try:
            # Prepare the prompt with system instructions and context
            system_prompt = self.get_system_prompt()
            
            if context:
                # Use safe serialization to avoid JSON errors
                context_str = f"\nContext: {self._serialize_context_safely(context)}"
            else:
                context_str = ""
            
            full_prompt = f"{system_prompt}{context_str}\n\nUser Input: {user_input}"
            
            # Generate response using Gemini
            response = self.llm_client.generate_content(
                contents=full_prompt,
            )
            
            # Store in conversation history
            self.conversation_history.append({
                "input": user_input,
                "output": response.text,
                "context": context
            })
            
            return {
                "success": True,
                "response": response.text,
                "raw_response": response
            }
            
        except Exception as e:
            logger.error(f"Error generating response for {self.name}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "response": None
            }
    
    def parse_json_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse JSON response from LLM output
        
        Args:
            response_text (str): Raw response text from LLM
            
        Returns:
            dict: Parsed JSON or error information
        """
        return JSONParser.parse_json_response(response_text)
    
    def reset_conversation(self):
        """Reset the conversation history"""
        self.conversation_history = []