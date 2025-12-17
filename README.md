# Phishing Evaluator

A console application that uses Azure OpenAI GPT models to evaluate the likelihood of an email message being a phishing attempt. The evaluation is based on comprehensive rules and scoring defined in a specialized prompt.

## Features

- **AI-Powered Analysis**: Leverages Azure OpenAI GPT models for intelligent phishing detection
- **Rule-Based Scoring**: Evaluates emails based on multiple criteria:
  - Sender analysis (suspicious addresses, domain spoofing)
  - Content red flags (urgent language, information requests)
  - Links and attachments (suspicious URLs, mismatched links)
  - Social engineering tactics (impersonation, urgency)
- **Detailed Reports**: Provides score, risk level, reasoning, red flags, and recommendations
- **Flexible Input**: Accepts email content from files or stdin
- **Configurable**: Supports environment variables and command-line arguments

## Requirements

- Python 3.8 or higher
- Azure OpenAI account with GPT model deployment
- Azure OpenAI API credentials

## Installation

### Using pip

```bash
pip install -r requirements.txt
```

### Using pip in development mode

```bash
pip install -e .
```

## Configuration

The application requires Azure OpenAI credentials. You can provide them via environment variables or command-line arguments.

### Environment Variables

Create a `.env` file in the project root (see `.env.example` for template):

```bash
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

### Command-Line Arguments

You can also provide credentials via command-line arguments:

```bash
python -m phishing_evaluator.main --endpoint https://your-resource.openai.azure.com/ \
                                   --api-key your-api-key \
                                   --deployment gpt-4 \
                                   email.txt
```

## Usage

### Evaluate an email from a file

```bash
python -m phishing_evaluator.main examples/phishing_example.txt
```

### Evaluate email from stdin

```bash
cat email.txt | python -m phishing_evaluator.main -
```

### Using the installed script (if installed with pip)

```bash
phishing-evaluator examples/phishing_example.txt
```

### Show verbose output with raw GPT response

```bash
python -m phishing_evaluator.main --verbose examples/phishing_example.txt
```

### Get help

```bash
python -m phishing_evaluator.main --help
```

## Scoring System

The application evaluates emails on a 0-100 scale:

### Scoring Categories

1. **Sender Analysis (0-25 points)**
   - Suspicious or mismatched sender address: +15 points
   - Known domain spoofing: +10 points
   - Free email service for business: +5 points

2. **Content Red Flags (0-30 points)**
   - Urgent/threatening language: +10 points
   - Requests for sensitive information: +15 points
   - Generic greetings: +5 points
   - Poor grammar/spelling: +5 points

3. **Links and Attachments (0-25 points)**
   - Suspicious URLs or URL shorteners: +15 points
   - Mismatched display text and actual URL: +10 points
   - Unexpected attachments: +10 points

4. **Social Engineering Tactics (0-20 points)**
   - Impersonation of authority: +10 points
   - Too good to be true offers: +10 points
   - Creating false sense of urgency: +5 points

### Risk Levels

- **0-20**: Very Low Risk - Likely legitimate
- **21-40**: Low Risk - Probably safe, minor concerns
- **41-60**: Medium Risk - Exercise caution
- **61-80**: High Risk - Likely phishing attempt
- **81-100**: Very High Risk - Almost certainly phishing

## Example Output

```
======================================================================
PHISHING EVALUATION RESULTS
======================================================================

SCORE: 85
RISK LEVEL: Very High Risk - Almost certainly phishing

----------------------------------------------------------------------
REASONING:
This email exhibits multiple critical phishing indicators. The sender 
domain 'paypal-verify.com' is not PayPal's legitimate domain, the 
message uses urgent threatening language about account limitation, 
and contains a suspicious URL that doesn't match PayPal's official domain.

RED FLAGS IDENTIFIED:
- Spoofed sender domain (paypal-verify.com vs paypal.com)
- Generic greeting ("Dear Valued Customer")
- Urgent language creating false sense of emergency
- Suspicious URL with different domain
- Threatening account suspension
- Request to click external link immediately

RECOMMENDATION:
DO NOT click any links in this email. This is a phishing attempt. 
Delete this email immediately and report it to PayPal's official 
phishing team at phishing@paypal.com. Never access your PayPal 
account from links in emails.

======================================================================
```

## Examples

The `examples/` directory contains sample emails for testing:

- `phishing_example.txt` - A typical phishing email (high risk)
- `legitimate_example.txt` - A legitimate email (low risk)

## Development

### Project Structure

```
phishing-evaluator/
├── phishing_evaluator/
│   ├── __init__.py
│   ├── main.py          # Console application entry point
│   └── evaluator.py     # Core phishing evaluation logic
├── examples/
│   ├── phishing_example.txt
│   └── legitimate_example.txt
├── .env.example
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Security Notice

This tool is designed to assist in identifying potential phishing emails but should not be the sole method of verification. Always:

- Verify sender addresses carefully
- Hover over links before clicking (don't click suspicious ones)
- Contact organizations directly using official channels
- Enable multi-factor authentication on important accounts
- Report suspected phishing to your IT security team

## License

This project is provided as-is for educational and security purposes.