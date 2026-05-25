#!/usr/bin/env python3
"""
Error Analyzer Agent - CLI Tool

AI-powered error log and stack trace analyzer using MiMo API.
Supports Python, Node.js, Java, Go, Rust, C#, Ruby, and PHP.

Usage:
    python analyzer.py <error_file>
    python analyzer.py --stdin          # Read from stdin
    python analyzer.py --json <file>    # JSON output
    python analyzer.py --batch <file>   # Analyze multiple errors
    python analyzer.py --lang <lang> <file>  # Override language detection

Examples:
    # Analyze a Python error
    python analyzer.py examples/python_error.txt

    # Pipe error from another command
    python script.py 2>&1 | python analyzer.py --stdin

    # Batch analyze with JSON output
    python analyzer.py --batch --json errors.log
"""

import argparse
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.analyzer import CoreAnalyzer
from lib.formatter import OutputFormatter
from lib.detector import LanguageDetector
from lib.categorizer import ErrorCategorizer


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="error-analyzer",
        description="AI-powered error log and stack trace analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s error.log                        Analyze a single error file
  %(prog)s --batch errors.log               Analyze multiple errors in a file
  %(prog)s --json error.log                 Output as JSON
  %(prog)s --batch --json errors.log        Batch analysis, JSON output
  %(prog)s --stdin                          Read error from stdin
  %(prog)s --detect error.log               Only detect language (no AI)
  %(prog)s --api-base http://host:port/v1 error.log  Custom API endpoint
        """,
    )

    parser.add_argument(
        "file",
        nargs="?",
        help="Path to error log/stack trace file",
    )
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read error input from stdin",
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Analyze multiple errors in one file",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON instead of formatted text",
    )
    parser.add_argument(
        "--detect",
        action="store_true",
        help="Only detect language/framework (no AI analysis)",
    )
    parser.add_argument(
        "--lang",
        type=str,
        choices=["python", "nodejs", "java", "go", "rust", "csharp", "ruby", "php"],
        help="Override automatic language detection",
    )
    parser.add_argument(
        "--api-base",
        type=str,
        default="http://localhost:20128/v1",
        help="MiMo API base URL (default: http://localhost:20128/v1)",
    )
    parser.add_argument(
        "--model",
        type=str,
        default="mimo-v2.5-pro",
        help="Model name (default: mimo-v2.5-pro)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    return parser.parse_args()


def read_input(args) -> str:
    """Read error input from file or stdin."""
    if args.stdin:
        if sys.stdin.isatty():
            print("Reading from stdin... (press Ctrl+D when done)", file=sys.stderr)
        return sys.stdin.read()

    if not args.file:
        print("Error: Please provide an error file or use --stdin", file=sys.stderr)
        sys.exit(1)

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        with open(args.file, "r", encoding="utf-8") as f:
            return f.read()
    except UnicodeDecodeError:
        with open(args.file, "r", encoding="latin-1") as f:
            return f.read()


def main():
    """Main entry point for the CLI."""
    args = parse_args()
    formatter = OutputFormatter(use_colors=not args.no_color and not args.json)

    # Read input
    input_text = read_input(args)
    if not input_text.strip():
        print("Error: Empty input", file=sys.stderr)
        sys.exit(1)

    # Detect-only mode
    if args.detect:
        detector = LanguageDetector()
        detection = detector.detect(input_text)
        error_type = detector.extract_error_type(input_text, detection["language"])
        file_refs = detector.extract_file_references(input_text)

        if args.json:
            print(json.dumps({
                "detection": detection,
                "error_type": error_type,
                "file_references": file_refs,
            }, indent=2))
        else:
            print(f"Language: {detection['language']}")
            print(f"Framework: {detection.get('framework', 'N/A')}")
            print(f"Confidence: {detection['confidence']}")
            print(f"Error Type: {error_type or 'N/A'}")
            print(f"File References: {len(file_refs)}")
            for ref in file_refs:
                line_info = f":{ref['line']}" if ref.get("line") else ""
                print(f"  → {ref['file']}{line_info}")
        return

    # Initialize analyzer
    analyzer = CoreAnalyzer(
        api_base=args.api_base,
        model=args.model,
    )

    # Override language detection if specified
    if args.lang:
        lang_map = {
            "python": "Python",
            "nodejs": "Node.js",
            "java": "Java",
            "go": "Go",
            "rust": "Rust",
            "csharp": "C#",
            "ruby": "Ruby",
            "php": "PHP",
        }
        original_detect = analyzer.detector.detect
        override_lang = lang_map.get(args.lang, args.lang)

        def patched_detect(text):
            result = original_detect(text)
            result["language"] = override_lang
            result["confidence"] = 1.0
            return result

        analyzer.detector.detect = patched_detect

    # Analyze
    if args.batch:
        results = analyzer.analyze_batch(input_text)

        if not results:
            print("No errors found in input.", file=sys.stderr)
            sys.exit(1)

        if args.json:
            print(formatter.format_batch_json(results))
        else:
            for i, result in enumerate(results):
                print(formatter.format_human(result, index=i))

            # Print summary
            summary = formatter._generate_summary(results)
            print(f"\n{'=' * 50}")
            print(f"📊 Batch Analysis Summary")
            print(f"{'=' * 50}")
            print(f"  Total errors: {summary['total_errors']}")
            print(f"  Languages: {', '.join(f'{k}({v})' for k, v in summary['languages'].items())}")
            print(f"  Categories: {', '.join(f'{k}({v})' for k, v in summary['categories'].items())}")
            print(f"  Severities: {', '.join(f'{k}({v})' for k, v in summary['severities'].items())}")
            print(f"  Highest severity: {summary['highest_severity'].upper()}")
    else:
        result = analyzer.analyze_single(input_text)

        if args.json:
            print(formatter.format_json(result))
        else:
            print(formatter.format_human(result))


if __name__ == "__main__":
    main()
