"""
Language and framework detection from stack trace patterns.

Supports: Python, Node.js, Java, Go, Rust, C#, Ruby, PHP
Each language has specific file extensions, error patterns, and stack trace formats.
"""

import re
from typing import Optional


# Detection rules ordered by specificity: (language, patterns, framework_patterns)
LANGUAGE_RULES = [
    {
        "language": "Python",
        "patterns": [
            r"Traceback \(most recent call last\)",
            r'File\s+".*\.py"',
            r"raise\s+\w+Error",
            r"\.py,?\s+line\s+\d+",
            r"During handling of the above exception",
            r"^\s+from\s+\w+.*import",
            r"NameError|TypeError|ValueError|ImportError|AttributeError",
        ],
        "framework_patterns": [
            (r"django|DJANGO", "Django"),
            (r"flask|Flask|FLASK", "Flask"),
            (r"FastAPI|fastapi", "FastAPI"),
            (r"pydantic|Pydantic", "Pydantic"),
            (r"celery|Celery", "Celery"),
        ],
        "file_ext": ".py",
    },
    {
        "language": "Node.js",
        "patterns": [
            r"at\s+.*\(.*\.js:\d+:\d+\)",
            r"at\s+.*\(.*\.ts:\d+:\d+\)",
            r"TypeError:\s",
            r"ReferenceError:\s",
            r"SyntaxError:\s",
            r"node_modules/",
            r"node:internal/",
            r"processTicksAndRejections",
        ],
        "framework_patterns": [
            (r"express|Express", "Express.js"),
            (r"react|React", "React"),
            (r"next|Next", "Next.js"),
            (r"nest|Nest", "NestJS"),
            (r"vue|Vue", "Vue.js"),
        ],
        "file_ext": ".js",
    },
    {
        "language": "Java",
        "patterns": [
            r"at\s+[\w.]+\(.*\.java:\d+\)",
            r"Exception\s+in\s+thread",
            r"Caused by:",
            r"java\.\w+\.\w+Exception",
            r"javax?\.\w+\.\w+Exception",
            r"at\s+sun\.reflect",
            r"at\s+org\.springframework",
        ],
        "framework_patterns": [
            (r"spring|Spring", "Spring"),
            (r"hibernate|Hibernate", "Hibernate"),
            (r"android|Android", "Android"),
            (r"jakarta|Jakarta", "Jakarta EE"),
            (r"maven|Gradle", "Maven/Gradle"),
        ],
        "file_ext": ".java",
    },
    {
        "language": "Go",
        "patterns": [
            r"goroutine\s+\d+\s+\[",
            r"runtime\.goexit",
            r"created\s+by\s+\w",
            r"panic\(",
            r"\.go:\d+\+",
            r"runtime error:",
            r"signal SIGSEGV",
        ],
        "framework_patterns": [
            (r"gin-gonic|gin", "Gin"),
            (r"echo|Echo", "Echo"),
            (r"fiber|Fiber", "Fiber"),
            (r"gorm|GORM", "GORM"),
        ],
        "file_ext": ".go",
    },
    {
        "language": "Rust",
        "patterns": [
            r"thread\s+'.*'\s+panicked",
            r"error\[E\d+\]",
            r"-->.*\.rs:\d+:\d+",
            r"cannot borrow",
            r"the trait.*is not implemented",
            r"move occurs because",
            r"does not implement the `Copy`",
        ],
        "framework_patterns": [
            (r"actix|Actix", "Actix"),
            (r"tokio|Tokio", "Tokio"),
            (r"serde|Serde", "Serde"),
            (r"clap|Clap", "Clap"),
        ],
        "file_ext": ".rs",
    },
    {
        "language": "C#",
        "patterns": [
            r"Unhandled exception",
            r"System\.\w+\.\w+Exception",
            r"\.cs:line\s+\d+",
            r"at\s+[\w.]+\.[\w.]+\(.*\.cs:\d+\)",
            r"System\.StackOverflowException",
            r"Microsoft\.AspNetCore",
        ],
        "framework_patterns": [
            (r"ASP\.NET|asp\.net", "ASP.NET"),
            (r"Entity\s*Framework", "Entity Framework"),
            (r"\.NET\s+Core|\.NET\s+6|\.NET\s+7|\.NET\s+8", ".NET Core"),
            (r"Blazor", "Blazor"),
        ],
        "file_ext": ".cs",
    },
    {
        "language": "Ruby",
        "patterns": [
            r"\.rb:\d+",
            r"\.erb:\d+",
            r"NoMethodError",
            r"unhandled error",
            r"\(\w+::\w+Error\)",
            r"Gem::LoadError",
            r"in `\w+'$",
        ],
        "framework_patterns": [
            (r"Rails|rails", "Ruby on Rails"),
            (r"Sinatra|sinatra", "Sinatra"),
            (r"Sidekiq|sidekiq", "Sidekiq"),
        ],
        "file_ext": ".rb",
    },
    {
        "language": "PHP",
        "patterns": [
            r"Fatal error:",
            r"Parse error:",
            r"Uncaught\s+\w+Exception",
            r"in\s+/.*\.php\s+on\s+line\s+\d+",
            r"PHP\s+Fatal\s+error",
            r"Stack trace:",
            r"  thrown in\s+.*\.php",
        ],
        "framework_patterns": [
            (r"Laravel|laravel", "Laravel"),
            (r"Symfony|symfony", "Symfony"),
            (r"WordPress|wordpress", "WordPress"),
            (r"Magento|magento", "Magento"),
        ],
        "file_ext": ".php",
    },
]


class LanguageDetector:
    """Detects programming language and framework from stack trace text."""

    def detect(self, text: str) -> dict:
        """
        Detect language, framework, and confidence from stack trace text.

        Args:
            text: The stack trace or error log content.

        Returns:
            dict with keys: language, framework, confidence, file_extension, indicators
        """
        results = []

        for rule in LANGUAGE_RULES:
            matched_patterns = []
            score = 0

            for pattern in rule["patterns"]:
                if re.search(pattern, text, re.IGNORECASE):
                    matched_patterns.append(pattern)
                    score += 1

            if score > 0:
                # Check for framework
                framework = None
                for fw_pattern, fw_name in rule["framework_patterns"]:
                    if re.search(fw_pattern, text, re.IGNORECASE):
                        framework = fw_name
                        score += 0.5
                        break

                confidence = min(score / len(rule["patterns"]), 1.0)
                results.append({
                    "language": rule["language"],
                    "framework": framework,
                    "confidence": confidence,
                    "file_extension": rule["file_ext"],
                    "matched_count": len(matched_patterns),
                    "indicators": matched_patterns,
                })

        if not results:
            return {
                "language": "Unknown",
                "framework": None,
                "confidence": 0.0,
                "file_extension": None,
                "indicators": [],
            }

        # Sort by confidence descending, then by matched count
        results.sort(key=lambda x: (x["confidence"], x["matched_count"]), reverse=True)
        best = results[0]

        return {
            "language": best["language"],
            "framework": best["framework"],
            "confidence": round(best["confidence"], 2),
            "file_extension": best["file_extension"],
            "indicators": best["indicators"],
        }

    def extract_error_type(self, text: str, language: str) -> Optional[str]:
        """
        Extract the primary error/exception type from the stack trace.

        Args:
            text: The stack trace text.
            language: Detected language.

        Returns:
            The error type string, or None if not found.
        """
        extractors = {
            "Python": [
                r"(\w+Error):?\s*(?:.*)",
                r"(Traceback \(most recent call last\))",
            ],
            "Node.js": [
                r"(TypeError|ReferenceError|SyntaxError|RangeError|URIError|EvalError):\s*(.*)",
                r"(Error):\s*(.*)",
            ],
            "Java": [
                r"(java\.\w+\.\w+Exception):?\s*(.*)",
                r"(\w+Exception):?\s*(.*)",
            ],
            "Go": [
                r"(panic:\s*.*)",
                r"(runtime error:.*)",
            ],
            "Rust": [
                r"(error\[E\d+\]:\s*.*)",
                r"(thread\s+'.*?'\s+panicked\s+at\s+'.*?')",
            ],
            "C#": [
                r"(System\.\w+\.\w+Exception):?\s*(.*)",
                r"(Unhandled exception):?\s*(.*)",
            ],
            "Ruby": [
                r"(\w+Error):\s*(.*)",
                r"(\(\w+::\w+Error\))",
            ],
            "PHP": [
                r"(Fatal error:\s*.*)",
                r"(Parse error:\s*.*)",
                r"(Uncaught\s+\w+Exception:\s*.*)",
            ],
        }

        for pattern in extractors.get(language, []):
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()

        return None

    def extract_file_references(self, text: str) -> list:
        """Extract file references from the stack trace."""
        file_refs = []
        patterns = [
            r'File\s+"([^"]+\.py)"',                      # Python
            r"at\s+\S+\s+\(([^)]+\.(?:js|ts)):(\d+)\)",   # Node.js
            r"at\s+[\w.]+\(([^)]+\.java):(\d+)\)",        # Java
            r"--> ([^:]+\.rs):(\d+):(\d+)",                 # Rust
            r"([^\s]+\.cs):line\s+(\d+)",                   # C#
            r"([^\s]+\.rb):(\d+)",                          # Ruby
            r"in\s+(/[^\s]+\.php)\s+on\s+line\s+(\d+)",   # PHP
            r"\t([^\s]+\.go):(\d+)",                         # Go
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text):
                groups = match.groups()
                file_ref = {"file": groups[0], "line": groups[1] if len(groups) > 1 else None}
                if file_ref not in file_refs:
                    file_refs.append(file_ref)

        return file_refs
