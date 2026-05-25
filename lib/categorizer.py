"""
Error categorization module.

Categorizes errors into types:
- syntax: Syntax/parse errors
- runtime: Runtime exceptions
- logic: Logic/algorithm errors
- dependency: Missing/incompatible dependencies
- config: Configuration/environment errors
- memory: Memory-related (OOM, leaks, segfaults)
- network: Network/connectivity errors
"""

import re
from typing import Optional


# Error type to category mappings with confidence weights
CATEGORY_RULES = {
    "syntax": {
        "keywords": [
            "SyntaxError", "ParseError", "parse error",
            "IndentationError", "unexpected token",
            "syntax error", "EOFError", "invalid syntax",
            "unexpected end of", "bracket mismatch",
            "expected", "unterminated string",
        ],
        "patterns": [
            r"syntax\s+error",
            r"unexpected\s+token",
            r"parse\s+error",
            r"indentation\s+error",
            r"invalid\s+syntax",
            r"unterminated",
            r"unexpected\s+end\s+of",
        ],
        "severity_base": "low",
    },
    "runtime": {
        "keywords": [
            "TypeError", "ValueError", "IndexError", "KeyError",
            "AttributeError", "NameError", "UnboundLocalError",
            "ArithmeticError", "ZeroDivisionError", "OverflowError",
            "RuntimeError", "NotImplementedError", "StopIteration",
            "AssertionError", "AssertionError", "EOFError",
            "DivisionByZeroError", "OverflowError", "FloatingPointError",
        ],
        "patterns": [
            r"type\s+error",
            r"value\s+error",
            r"index\s+(out\s+of\s+)?(range|bounds|bound)",
            r"key\s+error",
            r"attribute\s+error",
            r"name\s+error",
            r"not\s+defined",
            r"is\s+not\s+defined",
            r"object\s+has\s+no\s+attribute",
            r"list\s+index\s+out\s+of\s+range",
            r"undefined\s+is\s+not",
            r"null\s+reference",
            r"division\s+by\s+zero",
        ],
        "severity_base": "high",
    },
    "logic": {
        "keywords": [
            "AssertionError", "AssertionError",
            "LogicError", "InfiniteLoop",
            "DeadlockException",
        ],
        "patterns": [
            r"assert(ion)?\s+error",
            r"assertion\s+failed",
            r"logic\s+error",
            r"infinite\s+loop",
            r"deadlock",
        ],
        "severity_base": "medium",
    },
    "dependency": {
        "keywords": [
            "ImportError", "ModuleNotFoundError", "ImportError",
            "ModuleNotFoundError", "ModuleNotFound",
            "PackageNotFoundError", "RequirementNotFound",
            "npm ERR!", "MODULE_NOT_FOUND",
            "ClassNotFoundException", "NoClassDefFoundError",
            "Gem::LoadError", "LoadError",
            "ComposerError", "ClassNotFound",
            "go build", "cannot find module",
        ],
        "patterns": [
            r"no\s+module\s+named",
            r"cannot\s+import\s+name",
            r"module\s+not\s+found",
            r"import\s+error",
            r"class\s+not\s+found",
            r"no\s+such\s+file\s+or\s+directory",
            r"package\s+not\s+found",
            r"require\s+failed",
            r"MODULE_NOT_FOUND",
            r"gem\s+not\s+found",
            r"cargo.*not\s+found",
            r"no\s+matching\s+version",
            r"cannot\s+find\s+module",
            r"unresolved\s+dependency",
            r"missing\s+dependency",
        ],
        "severity_base": "medium",
    },
    "config": {
        "keywords": [
            "ConfigurationError", "ConfigError",
            "EnvironmentError", "PermissionError",
            "FileNotFoundError", "PermissionDenied",
            "AccessDenied", "EACCES", "ENOENT",
            "ConfigMissingError",
        ],
        "patterns": [
            r"configuration\s+error",
            r"config\s+file\s+not\s+found",
            r"permission\s+denied",
            r"access\s+denied",
            r"file\s+not\s+found",
            r"no\s+such\s+file\s+or\s+directory",
            r"could\s+not\s+read",
            r"failed\s+to\s+load\s+config",
            r"environment\s+variable",
            r"env\s+variable\s+not\s+set",
            r"invalid\s+configuration",
            r"missing\s+required\s+field",
            r"connection\s+refused\s+\(config",
            r"bad\s+credentials",
            r"unauthorized",
            r"authentication\s+failed",
        ],
        "severity_base": "medium",
    },
    "memory": {
        "keywords": [
            "MemoryError", "MemoryError", "OutOfMemoryError",
            "SegmentationFault", "SIGSEGV", "StackOverflow",
            "heap", "OOM", "malloc", "realloc",
            "RustOutofMemoryError",
        ],
        "patterns": [
            r"memory\s+error",
            r"out\s+of\s+memory",
            r"oom",
            r"segmentation\s+fault",
            r"sigsegv",
            r"stack\s+overflow",
            r"heap\s+(overflow|exhausted|full)",
            r"cannot\s+allocate",
            r"malloc\s+failed",
            r"allocation\s+failed",
            r"buffer\s+overflow",
            r"memory\s+exhausted",
            r"gc\s+heap\s+exhausted",
        ],
        "severity_base": "critical",
    },
    "network": {
        "keywords": [
            "ConnectionError", "TimeoutError", "URLError",
            "SocketError", "ConnectTimeoutError", "ReadTimeoutError",
            "ETIMEDOUT", "ECONNREFUSED", "ENOTFOUND",
            "ECONNRESET",
        ],
        "patterns": [
            r"connection\s+refused",
            r"connection\s+timed\s+out",
            r"connection\s+reset",
            r"connection\s+lost",
            r"network\s+(is\s+)?unreachable",
            r"no\s+route\s+to\s+host",
            r"host\s+not\s+found",
            r"dns\s+(resolution|lookup)\s+failed",
            r"ssl/tls\s+(handshake|error|certificate)",
            r"certificate\s+has\s+expired",
            r"ssl\s+handshake",
            r"econnrefused",
            r"etimedout",
            r"econnreset",
            r"socket\s+timeout",
            r"read\s+timed?\s*out",
            r"write\s+timed?\s*out",
            r"broken\s+pipe",
            r"eof\s+error",
        ],
        "severity_base": "high",
    },
}

# Severity escalation rules based on context
SEVERITY_ESCALATION = {
    "production": {"factor": 1.5, "context_keywords": ["production", "prod", "live"]},
    "critical_path": {"factor": 1.3, "context_keywords": ["main", "core", "critical"]},
    "recurrent": {"factor": 1.2, "context_keywords": ["again", "recurring", "frequent"]},
}


class ErrorCategorizer:
    """Categorizes errors by type and severity from stack trace text."""

    def categorize(self, text: str, error_type: Optional[str] = None) -> dict:
        """
        Categorize the error from stack trace text.

        Args:
            text: The stack trace or error log content.
            error_type: Optionally pre-extracted error type string.

        Returns:
            dict with keys: category, severity, confidence, category_scores
        """
        scores = {}
        text_lower = text.lower()

        for category, rules in CATEGORY_RULES.items():
            score = 0

            # Check keyword matches
            for keyword in rules["keywords"]:
                if keyword.lower() in text_lower:
                    score += 2

            # Check regex pattern matches
            for pattern in rules["patterns"]:
                if re.search(pattern, text_lower):
                    score += 3

            # Bonus for error_type match
            if error_type:
                for keyword in rules["keywords"]:
                    if keyword.lower() in error_type.lower():
                        score += 5

            scores[category] = score

        if not scores or max(scores.values()) == 0:
            return {
                "category": "runtime",  # Default fallback
                "severity": "medium",
                "confidence": 0.1,
                "category_scores": scores,
            }

        best_category = max(scores, key=scores.get)
        total_score = sum(scores.values())
        confidence = scores[best_category] / total_score if total_score > 0 else 0

        severity = self._assess_severity(
            best_category, text, error_type
        )

        return {
            "category": best_category,
            "severity": severity,
            "confidence": round(min(confidence, 1.0), 2),
            "category_scores": scores,
        }

    def _assess_severity(
        self, category: str, text: str, error_type: Optional[str] = None
    ) -> str:
        """
        Assess error severity considering context and category base severity.

        Severity levels: critical, high, medium, low
        """
        base_severity = CATEGORY_RULES.get(category, {}).get("severity_base", "medium")
        severity_order = ["low", "medium", "high", "critical"]
        current_idx = severity_order.index(base_severity)

        text_lower = text.lower()

        # Check for escalation factors
        for factor_name, config in SEVERITY_ESCALATION.items():
            for ctx_keyword in config["context_keywords"]:
                if ctx_keyword in text_lower:
                    current_idx = min(
                        current_idx + 1, len(severity_order) - 1
                    )
                    break

        # Special cases
        if any(sig in text_lower for sig in ["sigsegv", "segfault", "core dump"]):
            current_idx = len(severity_order) - 1  # critical
        elif "stack overflow" in text_lower:
            current_idx = max(current_idx, severity_order.index("high"))
        elif any(
            err in text_lower
            for err in ["out of memory", "oom", "memory exhausted"]
        ):
            current_idx = len(severity_order) - 1  # critical
        elif "connection refused" in text_lower and "production" in text_lower:
            current_idx = max(current_idx, severity_order.index("critical"))

        return severity_order[current_idx]

    def get_fix_suggestions(self, category: str, language: str) -> list:
        """
        Get common fix suggestions based on error category and language.

        Args:
            category: The error category.
            language: The programming language.

        Returns:
            List of fix suggestion strings.
        """
        suggestions = {
            "syntax": [
                "Check for missing brackets, quotes, or semicolons",
                "Verify indentation is consistent",
                "Use a linter/formatter to catch syntax issues",
                "Validate the syntax against the language specification",
            ],
            "runtime": [
                "Add null/undefined checks before accessing properties",
                "Validate input types and values",
                "Use try/except or try/catch to handle edge cases",
                "Add boundary checks for array/list indexing",
                "Verify variable initialization",
            ],
            "logic": [
                "Review the algorithm for correctness",
                "Add unit tests for edge cases",
                "Use debugging tools to trace execution flow",
                "Verify mathematical operations and comparisons",
            ],
            "dependency": [
                "Check if the package/module is installed",
                "Verify package version compatibility",
                "Update or reinstall dependencies",
                "Check import/module paths",
                "Review virtual environment or container setup",
            ],
            "config": [
                "Verify configuration file exists and is readable",
                "Check environment variables are set correctly",
                "Validate file permissions",
                "Review configuration syntax",
                "Check for typos in config keys",
            ],
            "memory": [
                "Profile memory usage to identify leaks",
                "Reduce memory-intensive operations",
                "Implement data pagination/streaming",
                "Check for circular references",
                "Increase memory limits if appropriate",
            ],
            "network": [
                "Verify network connectivity",
                "Check firewall rules and proxy settings",
                "Implement retry logic with exponential backoff",
                "Validate hostnames and ports",
                "Check SSL/TLS certificates",
                "Increase timeout values if appropriate",
            ],
        }

        base_suggestions = suggestions.get(category, ["Investigate the error context"])

        # Add language-specific suggestions
        lang_specific = {
            "Python": {
                "runtime": [
                    *base_suggestions,
                    "Use type hints and mypy for static type checking",
                    "Consider using dataclasses or pydantic for data validation",
                ],
                "dependency": [
                    *base_suggestions,
                    "Run: pip install -r requirements.txt",
                    "Check requirements.txt for version pinning",
                    "Verify virtualenv activation",
                ],
            },
            "Node.js": {
                "runtime": [
                    *base_suggestions,
                    "Use TypeScript for static type checking",
                    "Use optional chaining (?.) for null-safe access",
                    "Enable strict mode in tsconfig.json",
                ],
                "dependency": [
                    *base_suggestions,
                    "Run: npm install or yarn install",
                    "Delete node_modules and reinstall",
                    "Check package.json for version conflicts",
                ],
            },
            "Java": {
                "runtime": [
                    *base_suggestions,
                    "Use Optional for null safety",
                    "Add @NonNull/@Nullable annotations",
                    "Review object lifecycle and initialization order",
                ],
            },
            "Rust": {
                "runtime": [
                    *base_suggestions,
                    "Review ownership and borrowing rules",
                    "Consider using Option<T> or Result<T, E>",
                    "Use .unwrap_or() or .unwrap_or_default() for safer defaults",
                ],
            },
        }

        if language in lang_specific and category in lang_specific[language]:
            return lang_specific[language][category]

        return base_suggestions
