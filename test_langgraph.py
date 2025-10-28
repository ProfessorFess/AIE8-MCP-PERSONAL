#!/usr/bin/env python3
"""
Test script for the LangGraph MCP application
"""
import asyncio
import sys
from langgraph_app import create_mcp_workflow, MCPState
from langchain_core.messages import HumanMessage


async def test_workflow():
    """Test the LangGraph workflow with sample inputs"""
    print("Testing LangGraph MCP Application...")
    
    # Create workflow
    workflow = create_mcp_workflow()
    
    # Test cases
    test_cases = [
        "Search for information about Python programming",
        "Roll 2d20k1",
        "Find the card Lightning Bolt",
        "Generate a password with 16 characters",
        "Get a random Magic card"
    ]
    
    for i, test_input in enumerate(test_cases, 1):
        print(f"\n--- Test {i}: {test_input} ---")
        
        try:
            # Create initial state
            initial_state = MCPState(
                messages=[HumanMessage(content=test_input)]
            )
            
            # Run the workflow
            result = await workflow.ainvoke(initial_state)
            
            # Display results
            if result.messages:
                last_message = result.messages[-1]
                if hasattr(last_message, 'content'):
                    print(f"Response: {last_message.content[:200]}...")
                else:
                    print(f"Response: {str(last_message)[:200]}...")
            
            if result.tool_results:
                print(f"Tool used: {list(result.tool_results.keys())[0]}")
                
        except Exception as e:
            print(f"Error in test {i}: {str(e)}")
    
    print("\n✅ Testing completed!")


if __name__ == "__main__":
    asyncio.run(test_workflow())
