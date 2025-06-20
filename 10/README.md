# Product Search Tool

A console-based product search application that uses OpenAI's Tools/Function Calling to search a product dataset using natural language.

## ✨ Features

-   🚀 **Hybrid Interface**: Combines the power of natural language for searches with a simple, reliable `help` command for ease of use.
-   🧠 **AI-Powered Filtering**: OpenAI's AI doesn't just guess what you want—it directly reads the product list and returns only the items that match your request with advanced prompt engineering for precise results.
-   🔧 **Flexible & Modern**: Uses the latest `tools` format for OpenAI API calls with GPT-4.1-mini.
-   📊 **Clean, Structured Results**: Get a simple, easy-to-read list of matching products with intelligent handling of complex queries.

## ⚙️ Setup

1.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Provide OpenAI API Key**: You must provide your API key. You can do this in two ways:
    -   **Option 1: Command-Line Argument (Recommended)**
        ```bash
        python product_search_tool.py --api-key YOUR_API_KEY_HERE
        ```
    -   **Option 2: Environment Variable**
        ```bash
        # For Linux/macOS
        export OPENAI_API_KEY="YOUR_API_KEY_HERE"
        # For Windows (Command Prompt)
        set OPENAI_API_KEY="YOUR_API_KEY_HERE"
        # For Windows (PowerShell)
        $env:OPENAI_API_KEY = "YOUR_API_KEY_HERE"

        python product_search_tool.py
        ```

3.  **Product Data**: Ensure you have a `products.json` file in the same directory, or specify a custom path:
    ```bash
    python product_search_tool.py --api-key YOUR_KEY --products-file path/to/my_products.json
    ```

## 🚀 Usage

Once the setup is complete, run the tool and start asking questions!

### **Basic Search**
```bash
python product_search_tool.py --api-key YOUR_KEY
```
Then, at the prompt, type what you're looking for.

### **Example Queries**

You can ask simple or complex questions. The AI will understand the context and handle advanced queries like superlatives, precise numerical matching, and OR conditions.

**Note**: By default, the tool shows all matching products regardless of stock status (so you can see what's available). Only specify stock status if you want to filter by it.

-   `I need a smartphone under $800`
-   `Show me fitness equipment that's cheap and has good reviews`
-   `Find kitchen appliances that are in stock`
-   `What is the most expensive electronic device in stock?`
-   `I want a book with a rating of exactly 4.5`
-   `Show me electronics under $60`

The only built-in commands are:
- `help` - Shows a static help message with examples.
- `quit` (or `exit`) - Closes the program.

### **Saving Output to a File**

You can save your search sessions to a markdown file using the `--output-file` (or `-o`) argument.

When an output file is specified, the results will be printed to your console as usual, and they will *also* be saved to the specified file.

**Append to a file (Default behavior):**
```bash
python product_search_tool.py --api-key YOUR_KEY -o sample_outputs.md
```

**Overwrite a file:**
To clear the file before saving new results, use `--file-mode overwrite` (or `-m overwrite`).
```bash
python product_search_tool.py --api-key YOUR_KEY -o sample_outputs.md -m overwrite
```

## 🤔 How It Works

The magic is in how it uses OpenAI's AI:

1.  **You Ask a Question**: You type a query like "find me cheap headphones".
2.  **The Tool Prepares a Prompt**: It sends your question, along with the *entire* list of products from the JSON file, to the OpenAI API.
3.  **AI Performs the Search**: The AI uses chain-of-thought reasoning to understand complex queries and sifts through the product data. It handles numerical precision, superlatives, OR conditions, and contextual understanding.
4.  **AI Returns Structured Data**: Using a feature called "Tools", the AI returns a structured list of the exact products it found.
5.  **The Tool Displays the Results**: The application formats this list and prints it for you.

This approach means the filtering logic is handled by the AI's intelligence with sophisticated prompt engineering, not by manual `if/else` statements in the code.

## 📦 Dataset Structure

Your `products.json` file should be an array of objects, where each object has:
-   `name`: Product name (string)
-   `category`: Product category (string)
-   `price`: Price (number)
-   `rating`: Rating (number)
-   `in_stock`: Availability (boolean)