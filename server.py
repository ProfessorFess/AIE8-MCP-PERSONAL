from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
from dice_roller import DiceRoller

load_dotenv()

mcp = FastMCP("mcp-server")
client = TavilyClient(os.getenv("TAVILY_API_KEY"))

@mcp.tool()
def web_search(query: str) -> str:
    """Search the web for information about the given query"""
    search_results = client.get_search_context(query=query)
    return search_results

@mcp.tool()
def roll_dice(notation: str, num_rolls: int = 1) -> str:
    """Roll the dice with the given notation"""
    roller = DiceRoller(notation, num_rolls)
    return str(roller)

"""
Add your own tool here, and then use it through Cursor!
"""
@mcp.tool()
def generate_password(length: int = 12, include_symbols: bool = True) -> str:
    """Generate a random password with specified length and character options"""
    import string
    import secrets
    
    # Define character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    # Build character pool based on options
    chars = lowercase + uppercase + digits
    if include_symbols:
        chars += symbols
    
    # Generate password
    password = ''.join(secrets.choice(chars) for _ in range(length))
    
    return f"Generated password: {password}"

if __name__ == "__main__":
    mcp.run(transport="stdio")