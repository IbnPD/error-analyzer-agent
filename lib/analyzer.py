"""
Core analysis engine.

Connects to MiMo API to perform AI-powered error analysis,
integrating detection, categorization, and solution generation.
"""

import json
import re
from typing import Optional

from openai import OpenAI

from lib.detector import LanguageDetector
from lib.categorizer import ErrorCategorizer


# MiMo API configuration
DEFAULT_API_BASE = "http://localhost:20128/v1"
DEFAULT_MODEL = "mimo-v2.5-pro"


SYSTEM_PROMPT = """You are an expert error analyzer and software engineer. Given a stack trace or error log, provide a comprehensive analysis in JSON format.

Respond ONLY with valid JSON in this exact structure:
{
  "summary": "One-line summary of the error",
  "root_cause": "Detailed explanation of the root cause",
  "solution": "Step-by-step fix with code examples",
  "code_example": "Corrected code snippet or fix code",
  "prevention": "How to prevent this error in the future",
  "related_errors": ["list of related errors or potential cascading issues"]
}

Be specific, provide actual code fixes when possible, and reference the file/line numbers from the stack trace."""

SPLIT_PROMPT = """You are an error log parser. Given a log file that may contain multiple errors, split it into individual error entries.

Respond ONLY with valid JSON: a list of objects, each with:
{
  "index": 0,
  "content": "the full text of this individual error/stack trace"
}

If the input is a single error, return a list with one item."""

SEPARATOR_PATTERNS = [
    r"^={3,}\s*$",
    r"^-{3,}\s*$",
    r"^\*{3,}\s*$",
    r"^#{3,}\s*$",
    r"^---+BEGIN",
    r"^={3,}\s*ERROR\s*\d+",
    r"^Traceback \(most recent call last\):",
]


class CoreAnalyzer:
    """
    Main analysis engine that combines detection, categorization,
    and AI-powered analysis.
    """

    def __init__(
        self,
        api_base: str = DEFAULT_API_BASE,
        model: str = DEFAULT_MODEL,
        api_key: str = "not-needed",
    ):
        """
        Initialize the analyzer.

        Args:
            api_base: OpenAI-compatible API base URL.
            model: Model name to use.
            api_key: API key (default: not-needed for local endpoints).
        """
        self.client = OpenAI(base_url=api_base, api_key=api_key)
        self.model = model
        self.detector = LanguageDetector()
        self.categorizer = ErrorCategorizer()

    def analyze_single(self, error_text: str) -> dict:
        """
        Analyze a single error/stack trace.

        Args:
            error_text: The error text to analyze.

        Returns:
            Comprehensive analysis dict.
        """
        # Step 1: Detect language/framework
        detection = self.detector.detect(error_text)
        language = detection["language"]

        # Step 2: Extract error type
        error_type = self.detector.extract_error_type(error_text, language)

        # Step 3: Categorize
        categorization = self.categorizer.categorize(error_text, error_type)

        # Step 4: Get fix suggestions
        suggestions = self.categorizer.get_fix_suggestions(
            categorization["category"], language
        )

        # Step 5: Extract file references
        file_refs = self.detector.extract_file_references(error_text)

        # Step 6: Get AI-powered analysis
        ai_analysis = self._call_ai(error_text, detection, categorization)

        # Step 7: Compile result
        result = {
            "error_text": error_text,
            "detection": {
                "language": detection["language"],
                "framework": detection["framework"],
                "confidence": detection["confidence"],
                "file_extension": detection["file_extension"],
            },
            "error_type": error_type,
            "categorization": {
                "category": categorization["category"],
                "severity": categorization["severity"],
                "confidence": categorization["confidence"],
            },
            "file_references": file_refs,
            "ai_analysis": ai_analysis,
            "suggestions": suggestions,
        }

        return result

    def analyze_batch(self, log_text: str) -> list:
        """
        Analyze a log file that may contain multiple errors.

        Splits the log into individual errors and analyzes each.

        Args:
            log_text: The full log file content.

        Returns:
            List of analysis dicts.
        """
        # Try to split via AI first for complex logs
        split_errors = self._split_log(log_text)

        if len(split_errors) <= 1:
            # Fallback: try regex-based splitting
            split_errors = self._regex_split(log_text)

        results = []
        for i, error_text in enumerate(split_errors):
            if not error_text.strip():
                continue
            result = self.analyze_single(error_text)
            result["batch_index"] = i
            results.append(result)

        return results

    def _call_ai(
        self,
        error_text: str,
        detection: dict,
        categorization: dict,
    ) -> dict:
        """
        Call MiMo API for AI-powered analysis.

        Args:
            error_text: The error text.
            detection: Language detection result.
            categorization: Error categorization result.

        Returns:
            AI analysis dict.
        """
        user_message = f"""Analyze this error:

Language: {detection['language']} ({detection.get('framework', 'N/A')})
Category: {categorization['category']}
Severity: {categorization['severity']}

Error/Stack Trace:
```
{error_text}
```

Provide a detailed analysis with root cause, solution, and code example."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_message},
                ],
                temperature=0.3,
                max_tokens=2048,
            )

            content = response.choices[0].message.content
            return self._parse_ai_response(content)

        except Exception as e:
            return {
                "summary": f"AI analysis unavailable: {str(e)}",
                "root_cause": "Could not connect to MiMo API",
                "solution": "Ensure MiMo API is running at the configured endpoint",
                "code_example": "",
                "prevention": "Set up proper monitoring and logging",
                "related_errors": [],
                "raw_response": str(e),
            }

    def _parse_ai_response(self, content: str) -> dict:
        """Parse AI response, handling markdown code blocks."""
        # Try to extract JSON from markdown code block
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", content, re.DOTALL)
        if json_match:
            content = json_match.group(1)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON object in the response
            json_match = re.search(r"\{.*\}", content, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass

            return {
                "summary": content[:200] if content else "No analysis available",
                "root_cause": content if content else "No response from AI",
                "solution": "",
                "code_example": "",
                "prevention": "",
                "related_errors": [],
                "raw_response": content,
            }

    def _split_log(self, log_text: str) -> list:
        """Use AI to split a multi-error log into individual entries."""
        # If it's small, try to split with regex first
        if len(log_text) < 5000:
            return self._regex_split(log_text)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SPLIT_PROMPT},
                    {"role": "user", "content": log_text},
                ],
                temperature=0.1,
                max_tokens=4096,
            )

            content = response.choices[0].message.content
            json_match = re.search(r"\[.*\]", content, re.DOTALL)
            if json_match:
                entries = json.loads(json_match.group())
                return [entry.get("content", "") for entry in entries]
        except Exception:
            pass

        return self._regex_split(log_text)

    def _regex_split(self, log_text: str) -> list:
        """Split log using regex-based separator detection."""
        lines = log_text.split("\n")
        errors = []
        current_error = []

        for line in lines:
            is_separator = False
            for pattern in SEPARATOR_PATTERNS:
                if re.match(pattern, line, re.IGNORECASE):
                    is_separator = True
                    break

            if is_separator and current_error:
                errors.append("\n".join(current_error))
                current_error = []

            current_error.append(line)

        if current_error:
            errors.append("\n".join(current_error))

        return errors if errors else [log_text]
