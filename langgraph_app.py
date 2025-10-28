import asyncio
from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field


class MCPState(BaseModel):
    messages: List[Any] = Field(default_factory=list)
    current_query: Optional[str] = None
    tool_results: Dict[str, Any] = Field(default_factory=dict)
    user_intent: Optional[str] = None


class MCPClient:
    """Simple MCP client that directly imports and calls server functions"""
    
    def __init__(self):
        # Import the server module directly
        import sys
        import os
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Import server functions directly
        from server import web_search, roll_dice, search_card_by_name, get_random_card, get_set_info, generate_password
        self.tools = {
            "web_search": web_search,
            "roll_dice": roll_dice,
            "search_card_by_name": search_card_by_name,
            "get_random_card": get_random_card,
            "get_set_info": get_set_info,
            "generate_password": generate_password
        }
    
    async def call_tool(self, tool_name: str, **kwargs) -> str:
        """Call a tool directly"""
        try:
            if tool_name in self.tools:
                # Call the tool function directly
                result = self.tools[tool_name](**kwargs)
                return result
            else:
                return f"Tool {tool_name} not found"
        except Exception as e:
            return f"Error calling tool {tool_name}: {str(e)}"
    
    async def close(self):
        """No cleanup needed for direct imports"""
        pass


# Initialize MCP client
mcp_client = MCPClient()


def analyze_user_intent(state: MCPState) -> MCPState:
    """Analyze user intent and determine which MCP tool to use"""
    messages = state.messages
    if not messages:
        return state
    
    last_message = messages[-1]
    if isinstance(last_message, HumanMessage):
        query = last_message.content.lower()
        
        # Determine intent based on keywords
        if any(keyword in query for keyword in ["search", "find", "web", "look up"]):
            state.user_intent = "web_search"
        elif any(keyword in query for keyword in ["dice", "roll", "random"]):
            state.user_intent = "roll_dice"
        elif any(keyword in query for keyword in ["card", "magic", "mtg", "scryfall"]):
            if "random" in query:
                state.user_intent = "get_random_card"
            elif "set" in query:
                state.user_intent = "get_set_info"
            else:
                state.user_intent = "search_card_by_name"
        elif any(keyword in query for keyword in ["password", "generate"]):
            state.user_intent = "generate_password"
        else:
            state.user_intent = "web_search"  # Default to web search
    
    return state


async def execute_mcp_tool(state: MCPState) -> MCPState:
    """Execute the appropriate MCP tool based on user intent"""
    if not state.user_intent:
        return state
    
    messages = state.messages
    last_message = messages[-1]
    query = last_message.content
    
    try:
        if state.user_intent == "web_search":
            result = await mcp_client.call_tool("web_search", query=query)
        elif state.user_intent == "roll_dice":
            # Extract dice notation from query
            import re
            dice_match = re.search(r'(\d+d\d+(?:k\d+)?)', query)
            if dice_match:
                notation = dice_match.group(1)
                result = await mcp_client.call_tool("roll_dice", notation=notation)
            else:
                result = "Please specify dice notation (e.g., '2d20k1')"
        elif state.user_intent == "search_card_by_name":
            # Extract card name from query - look for common patterns
            import re
            # Remove common question words and extract the card name
            card_name = query.lower()
            # Remove common prefixes
            prefixes_to_remove = [
                r'what does the card\s+',
                r'what does\s+',
                r'find the card\s+',
                r'find\s+',
                r'search for the card\s+',
                r'search for\s+',
                r'card\s+',
                r'magic card\s+',
                r'mtg card\s+',
                r'show me\s+',
                r'tell me about\s+'
            ]
            
            for prefix in prefixes_to_remove:
                card_name = re.sub(prefix, '', card_name, flags=re.IGNORECASE)
            
            # Remove common suffixes
            suffixes_to_remove = [
                r'\s+do$',
                r'\s+do\?$',
                r'\s+work$',
                r'\s+work\?$',
                r'\s+do\s+.*$',
                r'\s+work\s+.*$'
            ]
            
            for suffix in suffixes_to_remove:
                card_name = re.sub(suffix, '', card_name, flags=re.IGNORECASE)
            
            card_name = card_name.strip()
            result = await mcp_client.call_tool("search_card_by_name", card_name=card_name)
        elif state.user_intent == "get_random_card":
            result = await mcp_client.call_tool("get_random_card")
        elif state.user_intent == "get_set_info":
            # Extract set code from query
            import re
            set_match = re.search(r'set\s+(\w+)', query)
            if set_match:
                set_code = set_match.group(1)
                result = await mcp_client.call_tool("get_set_info", set_code=set_code)
            else:
                result = "Please specify a set code (e.g., 'set DOM')"
        elif state.user_intent == "generate_password":
            # Extract password parameters
            import re
            length_match = re.search(r'(\d+)', query)
            length = int(length_match.group(1)) if length_match else 12
            
            include_symbols = "symbol" not in query or "symbol" in query
            result = await mcp_client.call_tool("generate_password", length=length, include_symbols=include_symbols)
        else:
            result = "I'm not sure how to help with that. Try asking about web search, dice rolling, Magic cards, or password generation."
        
        # Add tool result to state
        state.tool_results[state.user_intent] = result
        
        # Add AI response to messages
        ai_message = AIMessage(content=f"I used the {state.user_intent} tool to help you:\n\n{result}")
        state.messages.append(ai_message)
        
    except Exception as e:
        error_message = AIMessage(content=f"Sorry, I encountered an error: {str(e)}")
        state.messages.append(error_message)
    
    return state


def should_continue(state: MCPState) -> str:
    """Determine if we should continue processing or end"""
    if state.tool_results:
        return "end"
    return "end"


# Create the LangGraph workflow
def create_mcp_workflow():
    """Create and return the LangGraph workflow"""
    workflow = StateGraph(MCPState)
    
    # Add nodes
    workflow.add_node("analyze_intent", analyze_user_intent)
    workflow.add_node("execute_tool", execute_mcp_tool)
    
    # Add edges
    workflow.set_entry_point("analyze_intent")
    workflow.add_edge("analyze_intent", "execute_tool")
    workflow.add_conditional_edges(
        "execute_tool",
        should_continue,
        {
            "end": END
        }
    )
    
    return workflow.compile()


async def main():
    """Main function to run the LangGraph application"""
    print("🏗️ LangGraph MCP Application")
    print("Available tools: web search, dice rolling, Magic cards, password generation")
    print("Type 'quit' to exit\n")
    
    # Create workflow
    workflow = create_mcp_workflow()
    
    try:
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            # Create initial state
            initial_state = MCPState(
                messages=[HumanMessage(content=user_input)]
            )
            
            # Run the workflow
            result = await workflow.ainvoke(initial_state)
            
            # Display the AI response
            if hasattr(result, 'messages') and result.messages:
                last_message = result.messages[-1]
                if isinstance(last_message, AIMessage):
                    print(f"\nAI: {last_message.content}\n")
            elif isinstance(result, dict) and 'messages' in result:
                messages = result['messages']
                if messages:
                    last_message = messages[-1]
                    if isinstance(last_message, AIMessage):
                        print(f"\nAI: {last_message.content}\n")
    
    except KeyboardInterrupt:
        print("\nGoodbye!")
    
    finally:
        # Clean up MCP client
        await mcp_client.close()


if __name__ == "__main__":
    asyncio.run(main())
