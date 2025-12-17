"""Console application entry point for phishing evaluator."""

import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv

from phishing_evaluator.evaluator import PhishingEvaluator


def read_email_content(source: str) -> str:
    """Read email content from file or stdin.
    
    Args:
        source: File path or '-' for stdin
        
    Returns:
        Email content as string
    """
    if source == "-":
        return sys.stdin.read()
    
    email_file = Path(source)
    if not email_file.exists():
        raise FileNotFoundError(f"Email file not found: {source}")
    
    return email_file.read_text(encoding="utf-8")


def format_output(result: dict) -> str:
    """Format evaluation result for console output.
    
    Args:
        result: Dictionary containing evaluation results
        
    Returns:
        Formatted string for display
    """
    output = []
    output.append("=" * 70)
    output.append("PHISHING EVALUATION RESULTS")
    output.append("=" * 70)
    output.append("")
    
    if result["score"]:
        output.append(f"SCORE: {result['score']}")
    if result["risk_level"]:
        output.append(f"RISK LEVEL: {result['risk_level']}")
    
    output.append("")
    output.append("-" * 70)
    
    if result["reasoning"]:
        output.append("REASONING:")
        output.append(result["reasoning"])
        output.append("")
    
    if result["red_flags"]:
        output.append("RED FLAGS IDENTIFIED:")
        output.append(result["red_flags"])
        output.append("")
    
    if result["recommendation"]:
        output.append("RECOMMENDATION:")
        output.append(result["recommendation"])
    
    output.append("")
    output.append("=" * 70)
    
    return "\n".join(output)


def main():
    """Main entry point for the console application."""
    parser = argparse.ArgumentParser(
        description="Evaluate email messages for phishing attempts using Azure OpenAI GPT models.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Evaluate an email from a file
  phishing-evaluator email.txt
  
  # Evaluate email from stdin
  cat email.txt | phishing-evaluator -
  
  # Use custom Azure OpenAI configuration
  phishing-evaluator --endpoint https://myresource.openai.azure.com/ \\
                     --deployment gpt-4 \\
                     email.txt

Environment Variables:
  AZURE_OPENAI_ENDPOINT      Azure OpenAI endpoint URL
  AZURE_OPENAI_API_KEY       Azure OpenAI API key
  AZURE_OPENAI_DEPLOYMENT    Azure OpenAI deployment name
  AZURE_OPENAI_API_VERSION   Azure OpenAI API version (default: 2024-02-15-preview)
        """,
    )
    
    parser.add_argument(
        "email_source",
        help="Path to email file or '-' to read from stdin",
    )
    parser.add_argument(
        "--endpoint",
        help="Azure OpenAI endpoint URL (overrides AZURE_OPENAI_ENDPOINT)",
    )
    parser.add_argument(
        "--api-key",
        help="Azure OpenAI API key (overrides AZURE_OPENAI_API_KEY)",
    )
    parser.add_argument(
        "--deployment",
        help="Azure OpenAI deployment name (overrides AZURE_OPENAI_DEPLOYMENT)",
    )
    parser.add_argument(
        "--api-version",
        help="Azure OpenAI API version (overrides AZURE_OPENAI_API_VERSION)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Show full raw response from GPT",
    )
    
    args = parser.parse_args()
    
    # Load environment variables from .env file if present
    load_dotenv()
    
    try:
        # Read email content
        email_content = read_email_content(args.email_source)
        
        if not email_content.strip():
            print("Error: Email content is empty", file=sys.stderr)
            return 1
        
        # Initialize evaluator
        evaluator = PhishingEvaluator(
            endpoint=args.endpoint,
            api_key=args.api_key,
            deployment=args.deployment,
            api_version=args.api_version,
        )
        
        # Evaluate email
        print("Analyzing email...", file=sys.stderr)
        result = evaluator.evaluate(email_content)
        
        # Display results
        print(format_output(result))
        
        if args.verbose:
            print("\n" + "=" * 70)
            print("RAW RESPONSE:")
            print("=" * 70)
            print(result["raw_response"])
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Configuration Error: {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"Evaluation Error: {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        return 130
    except Exception as e:
        print(f"Unexpected Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
