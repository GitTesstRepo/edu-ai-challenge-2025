#!/usr/bin/env python3
"""
Product Search Tool
A console-based product search application that uses OpenAI API with function calling
to parse natural language queries and search through a products dataset.

Usage: python product_search_tool.py
"""

import json
import os
import sys
import argparse
from typing import List, Dict, Any, Optional
from openai import OpenAI

# Initialize OpenAI client
client = None

def load_products(filename: str = "products.json") -> List[Dict[str, Any]]:
    """Load products from JSON file."""
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}!")
        sys.exit(1)

def format_search_results(products: List[Dict]) -> str:
    """Format search results in a structured, readable format."""
    if not products:
        return "No products found matching your criteria."
    
    result = "Filtered Products:\n"
    
    for i, product in enumerate(products, 1):
        stock_status = "In Stock" if product['in_stock'] else "Out of Stock"
        result += f"{i}. {product['name']} - ${product['price']:.2f}, Rating: {product['rating']}, {stock_status}\n"
    
    return result.rstrip()  # Remove trailing newline

# Function definitions for OpenAI function calling
def get_function_definitions(products):
    """Generate tool definitions for the OpenAI API call."""
    return [
        {
            "type": "function",
            "function": {
                "name": "filter_and_return_products",
                "description": "Filter and return products that match the user's search criteria from the provided product list",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "matching_products": {
                            "type": "array",
                            "description": "Array of products that match the user's criteria",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "category": {"type": "string"},
                                    "price": {"type": "number"},
                                    "rating": {"type": "number"},
                                    "in_stock": {"type": "boolean"}
                                },
                                "required": ["name", "category", "price", "rating", "in_stock"]
                            }
                        }
                    },
                    "required": ["matching_products"]
                }
            }
        }
    ]

def process_user_query(user_input: str, products: List[Dict]) -> str:
    """
    Process user's natural language query using OpenAI function calling.
    OpenAI will directly filter and return matching products.
    
    Args:
        user_input: User's natural language search query
        products: List of all products
    
    Returns:
        Formatted search results
    """
    global client
    
    if not client:
        print("Error: OpenAI client not initialized. Please check your API key.")
        return "Error: Unable to process query."
    
    try:
        # Create messages for the conversation with product list
        products_json = json.dumps(products, indent=2)
        
        messages = [
            {
                "role": "system",
                "content": f"""You are a precise product search assistant. Your ONLY job is to filter the provided product list based on the user's query and call the `filter_and_return_products` tool with the result.

**Filtering Logic:**
*   **Default (AND):** When a user lists multiple criteria (e.g., "in stock" and "under $50"), a product must match ALL of them.
*   **"OR" queries:** When a user explicitly uses "or" or "either/or" (e.g., "Jacket or T-Shirt"), you must return products that match ANY of those specific options.

**Other Critical Rules:**
*   **Numerical Precision:** You must be absolutely exact with numbers. "rating of exactly 4.3" means `rating == 4.3`. "under 40" means `price < 40`. You MUST NOT include items with values that are merely close to the requested number.
*   **Superlatives ("most expensive", etc.):** Return ONLY the single product with the absolute highest/lowest value after all other filters are applied.
*   **Empty is OK:** If nothing matches, call the tool with an empty list `[]`. Do not guess.

You MUST call the tool. You MUST NOT respond with text.

Here are the available products:
{products_json}"""
            },
            {
                "role": "user",
                "content": user_input
            }
        ]
        
        # Make the API call with function calling
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=messages,
            tools=get_function_definitions(products),
            tool_choice="auto",
            temperature=0.1
        )
        
        # Check if the model wants to call a tool
        response_message = response.choices[0].message
        if response_message.tool_calls:
            tool_call = response_message.tool_calls[0]
            
            if tool_call.function.name == "filter_and_return_products":
                # Parse function arguments
                try:
                    function_args = json.loads(tool_call.function.arguments)
                    matching_products = function_args.get("matching_products", [])
                    
                    # Format and return results from the tool
                    return format_search_results(matching_products)
                    
                except json.JSONDecodeError:
                    return "Error: Failed to parse search results."
                except Exception as e:
                    return f"Error processing search results: {str(e)}"
        
        # If no tool call was made, it's an unexpected response
        return "Could not process the query. Please try rephrasing your search."
        
    except Exception as e:
        return f"Error processing query: {str(e)}"

def initialize_openai_client(api_key: str = None):
    """Initialize OpenAI client with API key."""
    global client
    
    # Use provided API key, or try environment variable
    if not api_key:
        api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("Error: No OpenAI API key provided.")
        print("Please provide your API key using --api-key parameter or set OPENAI_API_KEY environment variable.")
        return False
    
    try:
        client = OpenAI(api_key=api_key)
        # Test the connection with a simple call
        client.models.list()
        print("✅ OpenAI API connection successful!")
        return True
    except Exception as e:
        print(f"❌ Error connecting to OpenAI API: {str(e)}")
        return False

def show_help():
    """Display a static help message for the user."""
    help_text = """
Welcome to the AI Product Search Tool!

You can ask for products in plain English. The AI will understand your request and find matching items from the product list.

---
EXAMPLE QUERIES:
  - "I need a smartphone under $800"
  - "Show me fitness equipment that's cheap and has good reviews"
  - "Find kitchen appliances that are in stock"
  - "What kind of books do you have?"

---
COMMANDS:
  help      Show this help message.
  quit      Exit the program.
---
"""
    print(help_text)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Product Search Tool")
    parser.add_argument("--api-key", "-k", help="OpenAI API key")
    parser.add_argument("--products-file", "-p", default="products.json", help="Products JSON file")
    parser.add_argument("--output-file", "-o", help="File to save search outputs (e.g., sample_outputs.md)")
    parser.add_argument("--file-mode", "-m", choices=['append', 'overwrite'], default='append', help="Mode for the output file: 'append' or 'overwrite'")
    return parser.parse_args()

def handle_output(query: str, results: str, output_file: Optional[str]):
    """Handle the output, writing to console and optionally to a file."""
    # Always print to the console first for immediate feedback
    print(results)

    if output_file:
        # Format for markdown file
        file_content = f"## Search Query:\n```\n{query}\n```\n\n### Results:\n```\n{results}\n```\n\n---\n\n"
        try:
            with open(output_file, 'a', encoding='utf-8') as f:
                f.write(file_content)
            print(f"✅ Results also saved to {output_file}")
        except IOError as e:
            print(f"❌ Error writing to file {output_file}: {e}")

def main():
    """Main application loop."""
    # Parse command line arguments
    args = parse_arguments()
    
    print("🛍️  Welcome to the Product Search Tool!")
    print("=" * 50)

    # If overwrite mode is selected, clear the file once at the start
    if args.output_file and args.file_mode == 'overwrite':
        try:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                f.write(f"# Product Search Results\n\n") # Start with a title
            print(f"📋 Cleared {args.output_file} for new results.")
        except IOError as e:
            print(f"❌ Error clearing file {args.output_file}: {e}")
            sys.exit(1)
    
    # Initialize OpenAI client
    if not initialize_openai_client(args.api_key):
        print("Exiting due to API key issues.")
        sys.exit(1)
    
    # Load products
    print(f"📦 Loading products from {args.products_file}...")
    products = load_products(args.products_file)
    print(f"✅ Loaded {len(products)} products from database.")

    print("\n💡 Type 'help' for assistance or 'quit' to exit.")
    print("=" * 50)
    
    while True:
        try:
            user_input = input("\n🔍 Search Query: ").strip()
            
            if not user_input:
                continue
                
            # Handle built-in commands
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Thank you for using the Product Search Tool!")
                break
            
            if user_input.lower() == 'help':
                show_help()
                continue
            
            # Process the search query
            print("🤖 Processing your query...")
            results = process_user_query(user_input, products)
            
            # Handle output
            handle_output(user_input, results, args.output_file)
            
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using the Product Search Tool!")
            break
        except Exception as e:
            print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 