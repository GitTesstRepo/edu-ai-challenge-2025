# Service Analyzer

A powerful Python console application that generates comprehensive, structured service analysis reports from business, technical, and user perspectives using OpenAI's API. Analyze any service, product, or topic with a standardized 8-section format perfect for business intelligence and strategic planning.

## Key Capabilities

🎯 **Dual Input Support**: 
- **Known Services**: Analyze established companies/services (e.g., "Spotify", "Netflix", "Tesla")
- **Custom Descriptions**: Analyze service concepts from raw descriptions (e.g., "A music streaming service with AI recommendations")

## Features

- 📋 **Structured Analysis**: 8 standardized sections for consistent reporting
- 🎯 **Multi-Perspective**: Integrates business, technical, and user-focused viewpoints
- 🧠 **AI-Powered Detection**: OpenAI intelligently handles both known services and custom concepts
- 📝 **Markdown Output**: Professional, formatted reports ready for presentations
- 💾 **Flexible Output**: Terminal display, default file append, or custom file save
- 📊 **Sample Collection**: Build comprehensive demo files with multiple reports
- 🔧 **Configurable**: Multiple OpenAI models supported
- ⚡ **Efficient**: Single API call generates comprehensive multi-perspective analysis

## Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

3. **Set up OpenAI API Key** (choose one method):
   
   **Method 1: Environment Variable (Recommended)**
   ```powershell
   # Windows PowerShell
   $env:OPENAI_API_KEY="your-api-key-here"
   
   # Windows Command Prompt
   set OPENAI_API_KEY=your-api-key-here
   ```
   
   **Method 2: Command Line Parameter**
   ```powershell
   python main.py --api-key "your-api-key-here" "Your Topic"
   ```

## Usage

### Basic Usage
*Note: These examples assume `OPENAI_API_KEY` environment variable is set. If not, add `--api-key "your-key"` to any command.*

#### 1️⃣ Known Service Analysis
```powershell
# Analyze well-known companies/services
python main.py --console "Spotify"
python main.py "Netflix"
```

#### 2️⃣ "About Us" Text Analysis
```powershell
# Analyze company from their "About Us" description
python main.py "UnitedLex is the preeminent business partner for legal, delivering services that achieve value and drive growth for corporate legal departments and law firms..."
```

#### 3️⃣ Save to Custom File
```powershell
# Save to specific file (overwrites)
python main.py "Tesla" -o tesla_report.md
```

### Advanced Usage
```powershell
# Use with environment variable (recommended)
python main.py --console "Spotify"          # Terminal output
python main.py "Netflix"                     # Default file
python main.py "Tesla" -o tesla.md          # Custom file

# Analyze "About Us" text (use quotes for long descriptions)
python main.py --console "UnitedLex is the preeminent business partner for legal..."

# Building sample collection
python main.py --clear-samples "Spotify"    # Start fresh
python main.py "Netflix"                     # Append
python main.py "Amazon"                      # Append

# Use different OpenAI model
python main.py --model "gpt-4" --console "Microsoft"
```

### Example Inputs

#### Known Services/Companies:
- "Spotify"
- "Netflix" 
- "Tesla"
- "Amazon"
- "Microsoft"
- "OpenAI"
- "Zoom"
- "Slack"

#### Custom Service Descriptions:
- "A music streaming service with AI-powered recommendations"
- "Mobile app for tracking fitness goals with social sharing"
- "Cloud-based project management tool with real-time collaboration"
- "Video conferencing platform designed for remote education"
- "E-commerce marketplace focused on sustainable products"

#### Real-World "About Us" Text:
```
"UnitedLex is the preeminent business partner for legal, delivering services that achieve value and drive growth for corporate legal departments and law firms in the areas of litigation and investigations, intellectual property, legal operations, and incident response. Founded in 2006, we co-create solutions that mitigate risk, drive revenue, and optimize business investment-transforming the legal function into a catalyst for success. Our team of 2,000+ legal and business professionals, data analysts, technologists, and engineers supports our clients from operational centers around the world."
```

## Sample Output

The application generates structured reports with exactly 8 sections:

```markdown
# Comprehensive Analysis Report: Spotify

*Generated on: 2025-06-17 23:53:50*

---

## 1. Brief History  
Spotify was founded in 2006 by Daniel Ek and Martin Lorentzon...

## 2. Target Audience  
Primary targets include music listeners aged 16-35...

## 3. Core Features  
- On-demand music streaming with personalized playlists
- Podcast streaming and exclusive content...

## 4. Unique Selling Points  
- Extensive music and podcast library with 100M+ tracks
- Highly personalized user experience...

## 5. Business Model  
Freemium model with premium subscriptions and advertising...

## 6. Tech Stack Insights  
Microservices architecture built on Java, Python, Google Cloud...

## 7. Perceived Strengths  
Strong brand recognition, vast content library...

## 8. Perceived Weaknesses  
High royalty costs, licensing restrictions...
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `topic` | **Required**. Service name or topic to analyze | `"Spotify"` |
| `--api-key` | OpenAI API key (if not in environment) | `--api-key "sk-..."` |
| `--console` | Display output in terminal instead of saving to file | `--console` |
| `--output`, `-o` | Save report to custom file (default: sample_outputs.md) | `-o custom_report.md` |
| `--model` | OpenAI model to use (default: gpt-4.1-mini) | `--model "gpt-4"` |
| `--clear-samples` | Clear sample_outputs.md before adding new report | `--clear-samples` |

## Report Structure

Every report includes exactly these 8 sections in order:

1. **Brief History** - Founding year, milestones, etc.
2. **Target Audience** - Primary user segments
3. **Core Features** - Top 2–4 key functionalities
4. **Unique Selling Points** - Key differentiators
5. **Business Model** - How the service makes money
6. **Tech Stack Insights** - Any hints about technologies used
7. **Perceived Strengths** - Mentioned positives or standout features
8. **Perceived Weaknesses** - Cited drawbacks or limitations

## Getting Your OpenAI API Key

1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Sign up or log in to your account
3. Navigate to **API Keys** section
4. Create a new API key
5. Copy the key and use it with this application

## Error Handling

The application provides clear error messages for common issues:
- Missing API key
- Invalid API key
- Network connectivity issues
- API rate limits
- Missing dependencies

## Requirements

- Python 3.7+
- OpenAI API key
- Internet connection
- Dependencies listed in `requirements.txt`

## Troubleshooting

**"OpenAI library not installed"**
```powershell
pip install -r requirements.txt
```

**"OpenAI API key not found"**
- Set environment variable: `$env:OPENAI_API_KEY="your-key"`
- Or use `--api-key` parameter

**"Rate limit exceeded"**
- Wait a moment and try again
- Consider upgrading your OpenAI plan

**"Project does not have access to model"**
- Add billing information to your OpenAI account
- Try a different model with `--model` parameter

## Output Options

### 📺 Terminal Output
```powershell
python main.py --console "Spotify"
```
- Displays report directly in terminal
- No file is saved
- Perfect for quick analysis

### 📁 Default File (sample_outputs.md)
```powershell
python main.py "Netflix"
```
- Automatically appends to `sample_outputs.md`
- Builds a collection of multiple reports
- Adds separators between reports
- Great for building demo files

### 📄 Custom File
```powershell
python main.py "Tesla" -o tesla_report.md
```
- Saves to specified filename
- Overwrites existing file
- Perfect for individual reports

### 🗑️ Clear and Start Fresh
```powershell
python main.py --clear-samples "First Report"
```
- Clears `sample_outputs.md` before adding new report
- Useful for starting a new collection

## License

This project is open source. Feel free to use, modify, and distribute as needed.

## Contributing

Contributions welcome! Please feel free to submit issues, feature requests, or pull requests. 