"""Phishing evaluator using Azure OpenAI GPT models."""

import os
from typing import Dict, Optional
from openai import AzureOpenAI


PHISHING_EVALUATION_PROMPT = """You are a cybersecurity expert analyzing emails for phishing attempts. 
Evaluate the following email and provide a phishing likelihood score based on these criteria:

SCORING RULES (0-100):
1. Sender Analysis (0-25 points):
   - Suspicious or mismatched sender address: +15 points
   - Known domain spoofing: +10 points
   - Free email service for business: +5 points

2. Content Red Flags (0-30 points):
   - Urgent/threatening language: +10 points
   - Requests for sensitive information: +15 points
   - Generic greetings (e.g., "Dear Customer"): +5 points
   - Poor grammar/spelling: +5 points

3. Links and Attachments (0-25 points):
   - Suspicious URLs or URL shorteners: +15 points
   - Mismatched display text and actual URL: +10 points
   - Unexpected attachments: +10 points

4. Social Engineering Tactics (0-20 points):
   - Impersonation of authority: +10 points
   - Too good to be true offers: +10 points
   - Creating false sense of urgency: +5 points

SCORE INTERPRETATION:
- 0-20: Very Low Risk - Likely legitimate
- 21-40: Low Risk - Probably safe, minor concerns
- 41-60: Medium Risk - Exercise caution
- 61-80: High Risk - Likely phishing attempt
- 81-100: Very High Risk - Almost certainly phishing

Analyze the email below and provide:
1. A numerical score (0-100)
2. Risk level classification
3. Detailed reasoning for the score, explaining which rules triggered
4. Specific red flags identified
5. Recommendations for the recipient

EMAIL TO ANALYZE:
{email_content}

Provide your response in the following format:
SCORE: [numerical score]
RISK LEVEL: [classification]
REASONING: [detailed explanation]
RED FLAGS: [list of identified issues]
RECOMMENDATION: [action to take]
"""


class PhishingEvaluator:
    """Evaluates emails for phishing likelihood using Azure OpenAI."""

    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment: Optional[str] = None,
        api_version: Optional[str] = None,
    ):
        """Initialize the phishing evaluator.
        
        Args:
            endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            deployment: Azure OpenAI deployment name
            api_version: Azure OpenAI API version
        """
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment = deployment or os.getenv("AZURE_OPENAI_DEPLOYMENT")
        self.api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")

        if not all([self.endpoint, self.api_key, self.deployment]):
            raise ValueError(
                "Azure OpenAI configuration missing. Please provide endpoint, api_key, and deployment "
                "either as arguments or via environment variables."
            )

        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
        )

    def evaluate(self, email_content: str) -> Dict[str, str]:
        """Evaluate an email for phishing likelihood.
        
        Args:
            email_content: The email content to evaluate
            
        Returns:
            Dictionary containing the evaluation results
        """
        prompt = PHISHING_EVALUATION_PROMPT.format(email_content=email_content)

        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a cybersecurity expert specializing in phishing detection.",
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1000,
            )

            result = response.choices[0].message.content
            return self._parse_response(result)

        except Exception as e:
            raise RuntimeError(f"Error evaluating email: {str(e)}")

    def _parse_response(self, response: str) -> Dict[str, str]:
        """Parse the GPT response into structured data.
        
        Args:
            response: Raw response from GPT
            
        Returns:
            Dictionary with parsed fields
        """
        result = {
            "score": "",
            "risk_level": "",
            "reasoning": "",
            "red_flags": "",
            "recommendation": "",
            "raw_response": response,
        }

        lines = response.strip().split("\n")
        current_section = None

        for line in lines:
            line = line.strip()
            if line.startswith("SCORE:"):
                result["score"] = line.replace("SCORE:", "").strip()
                current_section = "score"
            elif line.startswith("RISK LEVEL:"):
                result["risk_level"] = line.replace("RISK LEVEL:", "").strip()
                current_section = "risk_level"
            elif line.startswith("REASONING:"):
                result["reasoning"] = line.replace("REASONING:", "").strip()
                current_section = "reasoning"
            elif line.startswith("RED FLAGS:"):
                result["red_flags"] = line.replace("RED FLAGS:", "").strip()
                current_section = "red_flags"
            elif line.startswith("RECOMMENDATION:"):
                result["recommendation"] = line.replace("RECOMMENDATION:", "").strip()
                current_section = "recommendation"
            elif line and current_section:
                # Continue multi-line sections
                if result[current_section]:
                    result[current_section] += " " + line
                else:
                    result[current_section] = line

        return result
