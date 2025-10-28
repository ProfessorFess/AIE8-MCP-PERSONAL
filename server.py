from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
import os
import requests
import json
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
Scryfall API Tools for Magic: The Gathering card database
"""
@mcp.tool()
def search_card_by_name(card_name: str, fuzzy: bool = True) -> str:
    """Search for a Magic: The Gathering card by name using Scryfall API"""
    try:
        if fuzzy:
            url = f"https://api.scryfall.com/cards/named?fuzzy={card_name}"
        else:
            url = f"https://api.scryfall.com/cards/named?exact={card_name}"
        
        response = requests.get(url)
        response.raise_for_status()
        card_data = response.json()
        
        # Format the response nicely
        result = f"**{card_data.get('name', 'Unknown')}**\n"
        result += f"Mana Cost: {card_data.get('mana_cost', 'N/A')}\n"
        result += f"Type: {card_data.get('type_line', 'N/A')}\n"
        result += f"Oracle Text: {card_data.get('oracle_text', 'N/A')}\n"
        result += f"Power/Toughness: {card_data.get('power', 'N/A')}/{card_data.get('toughness', 'N/A')}\n"
        result += f"Set: {card_data.get('set_name', 'N/A')} ({card_data.get('set', 'N/A')})\n"
        result += f"Rarity: {card_data.get('rarity', 'N/A')}\n"
        if 'image_uris' in card_data and 'normal' in card_data['image_uris']:
            result += f"Image: {card_data['image_uris']['normal']}\n"
        
        return result
    except requests.exceptions.RequestException as e:
        return f"Error searching for card '{card_name}': {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool()
def search_cards(query: str, page: int = 1) -> str:
    """Search for Magic: The Gathering cards using Scryfall's search API"""
    try:
        url = f"https://api.scryfall.com/cards/search?q={query}&page={page}"
        response = requests.get(url)
        response.raise_for_status()
        search_data = response.json()
        
        if not search_data.get('data'):
            return f"No cards found for query: '{query}'"
        
        result = f"Found {search_data.get('total_cards', 0)} cards for query: '{query}'\n\n"
        
        for i, card in enumerate(search_data['data'][:10], 1):  # Show first 10 results
            result += f"{i}. **{card.get('name', 'Unknown')}**\n"
            result += f"   Mana Cost: {card.get('mana_cost', 'N/A')}\n"
            result += f"   Type: {card.get('type_line', 'N/A')}\n"
            result += f"   Set: {card.get('set_name', 'N/A')}\n\n"
        
        if search_data.get('has_more'):
            result += f"... and {search_data.get('total_cards', 0) - 10} more cards available"
        
        return result
    except requests.exceptions.RequestException as e:
        return f"Error searching cards with query '{query}': {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool()
def get_random_card() -> str:
    """Get a random Magic: The Gathering card from Scryfall"""
    try:
        response = requests.get("https://api.scryfall.com/cards/random")
        response.raise_for_status()
        card_data = response.json()
        
        result = f"**Random Card: {card_data.get('name', 'Unknown')}**\n"
        result += f"Mana Cost: {card_data.get('mana_cost', 'N/A')}\n"
        result += f"Type: {card_data.get('type_line', 'N/A')}\n"
        result += f"Oracle Text: {card_data.get('oracle_text', 'N/A')}\n"
        result += f"Power/Toughness: {card_data.get('power', 'N/A')}/{card_data.get('toughness', 'N/A')}\n"
        result += f"Set: {card_data.get('set_name', 'N/A')} ({card_data.get('set', 'N/A')})\n"
        result += f"Rarity: {card_data.get('rarity', 'N/A')}\n"
        if 'image_uris' in card_data and 'normal' in card_data['image_uris']:
            result += f"Image: {card_data['image_uris']['normal']}\n"
        
        return result
    except requests.exceptions.RequestException as e:
        return f"Error getting random card: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool()
def get_card_by_id(card_id: str) -> str:
    """Get a specific Magic: The Gathering card by its Scryfall ID"""
    try:
        response = requests.get(f"https://api.scryfall.com/cards/{card_id}")
        response.raise_for_status()
        card_data = response.json()
        
        result = f"**{card_data.get('name', 'Unknown')}**\n"
        result += f"Mana Cost: {card_data.get('mana_cost', 'N/A')}\n"
        result += f"Type: {card_data.get('type_line', 'N/A')}\n"
        result += f"Oracle Text: {card_data.get('oracle_text', 'N/A')}\n"
        result += f"Power/Toughness: {card_data.get('power', 'N/A')}/{card_data.get('toughness', 'N/A')}\n"
        result += f"Set: {card_data.get('set_name', 'N/A')} ({card_data.get('set', 'N/A')})\n"
        result += f"Rarity: {card_data.get('rarity', 'N/A')}\n"
        result += f"Scryfall ID: {card_data.get('id', 'N/A')}\n"
        if 'image_uris' in card_data and 'normal' in card_data['image_uris']:
            result += f"Image: {card_data['image_uris']['normal']}\n"
        
        return result
    except requests.exceptions.RequestException as e:
        return f"Error getting card with ID '{card_id}': {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

@mcp.tool()
def get_set_info(set_code: str) -> str:
    """Get information about a Magic: The Gathering set by its code"""
    try:
        response = requests.get(f"https://api.scryfall.com/sets/{set_code}")
        response.raise_for_status()
        set_data = response.json()
        
        result = f"**{set_data.get('name', 'Unknown')}** ({set_data.get('code', 'N/A')})\n"
        result += f"Release Date: {set_data.get('released_at', 'N/A')}\n"
        result += f"Set Type: {set_data.get('set_type', 'N/A')}\n"
        result += f"Card Count: {set_data.get('card_count', 'N/A')}\n"
        result += f"Digital: {'Yes' if set_data.get('digital', False) else 'No'}\n"
        result += f"Foil Only: {'Yes' if set_data.get('foil_only', False) else 'No'}\n"
        if 'icon_svg_uri' in set_data:
            result += f"Set Icon: {set_data['icon_svg_uri']}\n"
        
        return result
    except requests.exceptions.RequestException as e:
        return f"Error getting set info for '{set_code}': {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

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