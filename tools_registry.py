"""
tools_registry.py
A decorator-driven tool registry for modular AI skill extensions and external API integrations.
"""
import inspect
from typing import Callable, Dict, Any, List, Optional

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Dict[str, Any]] = {}

    def register_tool(self, name: Optional[str] = None, description: Optional[str] = None, parameters: Optional[Dict[str, Any]] = None):
        """Decorator to register a function as an AI agent tool."""
        def decorator(func: Callable):
            tool_name = name or func.__name__
            tool_desc = description or (func.__doc__.strip() if func.__doc__ else f"Execute {tool_name}")
            
            # Default param schema if not provided
            param_schema = parameters or {
                "type": "object",
                "properties": {},
                "required": []
            }
            
            self._tools[tool_name] = {
                "func": func,
                "name": tool_name,
                "description": tool_desc,
                "parameters": param_schema
            }
            return func
        return decorator

    def execute(self, name: str, **kwargs) -> Any:
        """Executes a registered tool by name with keyword arguments."""
        if name not in self._tools:
            return f"Error: Tool '{name}' is not registered in the system."
        
        tool = self._tools[name]
        try:
            return tool["func"](**kwargs)
        except TypeError as e:
            # Fallback if arguments differ slightly
            func = tool["func"]
            sig = inspect.signature(func)
            valid_args = {k: v for k, v in kwargs.items() if k in sig.parameters}
            return func(**valid_args)
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """Returns tool definitions in OpenAI Function Call format."""
        openai_tools = []
        for name, info in self._tools.items():
            openai_tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": info["description"],
                    "parameters": info["parameters"]
                }
            })
        return openai_tools

    def get_anthropic_tools(self) -> List[Dict[str, Any]]:
        """Returns tool definitions in Anthropic Claude format."""
        anthropic_tools = []
        for name, info in self._tools.items():
            anthropic_tools.append({
                "name": name,
                "description": info["description"],
                "input_schema": info["parameters"]
            })
        return anthropic_tools

    def get_tools_info(self) -> List[Dict[str, Any]]:
        """Returns metadata list of tools for external API documentation."""
        return [
            {
                "name": name,
                "description": info["description"],
                "parameters": info["parameters"]
            }
            for name, info in self._tools.items()
        ]

# Global Singleton Registry Instance
registry = ToolRegistry()
register_tool = registry.register_tool
