#!/usr/bin/env python3
"""
Service Analyzer
A console application that generates comprehensive reports from business, technical, and user perspectives
using OpenAI API.
"""

import argparse
import os
import sys
from datetime import datetime
from typing import Optional

try:
    from openai import OpenAI
except ImportError:
    print("Error: OpenAI library not installed. Please run: pip install -r requirements.txt")
    sys.exit(1)


class ReportGenerator:
    """Main class for generating comprehensive service analysis reports from business, technical, and user perspectives using OpenAI API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the report generator with OpenAI API key."""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Please set OPENAI_API_KEY environment variable or pass it as parameter.")
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4.1-mini"
    
    def generate_comprehensive_analysis(self, topic: str) -> str:
        """Generate comprehensive analysis from business, technical, and user-focused perspectives."""
        prompt = f"""
        Analyze "{topic}" from BUSINESS, TECHNICAL, and USER-FOCUSED perspectives. Your response must include ONLY these sections in EXACT order:

        ## 1. Brief History
        - Founding year, milestones, etc.

        ## 2. Target Audience
        - Primary user segments

        ## 3. Core Features
        - Top 2–4 key functionalities

        ## 4. Unique Selling Points
        - Key differentiators

        ## 5. Business Model
        - How the service makes money

        ## 6. Tech Stack Insights
        - Any hints about technologies used

        ## 7. Perceived Strengths
        - Mentioned positives or standout features

        ## 8. Perceived Weaknesses
        - Cited drawbacks or limitations

        Include ONLY these 8 sections. Do not add any other sections or analysis.
        Ensure each section incorporates insights from business, technical, and user-focused viewpoints where relevant.
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,  # Increased for more comprehensive analysis
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating comprehensive analysis: {str(e)}"


    
    def generate_comprehensive_report(self, topic: str) -> str:
        """Generate a comprehensive report combining business, technical, and user perspectives."""
        print(f"Generating comprehensive report for: {topic}")
        print("This may take a moment...")
        
        # Generate comprehensive analysis
        print("⏳ Analyzing from business, technical, and user perspectives...")
        analysis = self.generate_comprehensive_analysis(topic)
        
        # Combine into comprehensive report
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"""# Comprehensive Analysis Report: {topic}

*Generated on: {timestamp}*

---

{analysis}

---

*Report generated using OpenAI API - Service Analyzer*
"""
        
        return report


def main():
    """Main function to handle command line arguments and generate reports."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive service analysis reports from business, technical, and user perspectives using OpenAI API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Known services analysis
  python main.py "Spotify"
  python main.py "Netflix"
  python main.py --console "Tesla"
  
  # "About Us" text analysis
  python main.py "UnitedLex is the preeminent business partner for legal..."
  
  # Output options
  python main.py "Amazon" -o amazon_report.md
  python main.py --clear-samples "Microsoft"
  
  # With API key parameter
  python main.py --api-key YOUR_API_KEY "OpenAI"
        """
    )
    
    parser.add_argument(
        "topic",
        help="The service name or topic to analyze (enclose in quotes if multiple words)"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI API key (optional if OPENAI_API_KEY environment variable is set)"
    )
    
    parser.add_argument(
        "--output",
        "-o",
        help="Output file path (optional - defaults to sample_outputs.md)"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-4.1-mini",
        help="OpenAI model to use (default: gpt-4.1-mini)"
    )
    
    parser.add_argument(
        "--clear-samples",
        action="store_true",
        help="Clear sample_outputs.md before adding new report"
    )
    
    parser.add_argument(
        "--console",
        action="store_true",
        help="Display output in terminal instead of saving to file"
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize report generator
        generator = ReportGenerator(api_key=args.api_key)
        generator.model = args.model
        
        # Generate comprehensive report
        report = generator.generate_comprehensive_report(args.topic)
        
        # Output report
        if args.console:
            # Display in terminal
            print("\n" + "="*80)
            print(report)
            print("="*80)
            print("📊 Report displayed in terminal")
        else:
            output_file = args.output or "sample_outputs.md"
            
            # If using default sample_outputs.md, append instead of overwrite
            if output_file == "sample_outputs.md":
                # Clear file if requested
                if args.clear_samples:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(report)
                    print(f"✅ Report saved to: {output_file} (file cleared)")
                else:
                    # Check if file exists and add separator
                    try:
                        with open(output_file, 'r', encoding='utf-8') as f:
                            existing_content = f.read().strip()
                        if existing_content:
                            separator = "\n\n" + "="*80 + "\n\n"
                            report = separator + report
                    except FileNotFoundError:
                        pass  # File doesn't exist yet, no separator needed
                    
                    # Append to sample_outputs.md
                    with open(output_file, 'a', encoding='utf-8') as f:
                        f.write(report)
                    print(f"✅ Report appended to: {output_file}")
            else:
                # For custom files, overwrite as usual
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(report)
                print(f"✅ Report saved to: {output_file}")
            
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("\nPlease ensure you have set your OpenAI API key:")
        print("  Method 1: Set environment variable - export OPENAI_API_KEY='your-key-here'")
        print("  Method 2: Use --api-key parameter - python main.py --api-key 'your-key-here' 'your topic'")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 