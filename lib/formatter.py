"""
Output formatting module.

Formats analysis results as:
- Human-readable terminal output
- Machine-readable JSON
"""

import json
from typing import Optional


# ANSI color codes
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    @classmethod
    def disable(cls):
        """Disable colors for non-terminal output."""
        cls.RED = cls.GREEN = cls.YELLOW = cls.BLUE = ""
        cls.MAGENTA = cls.CYAN = cls.BOLD = cls.DIM = cls.RESET = ""


# Severity colors
SEVERITY_COLORS = {
    "critical": Colors.RED + Colors.BOLD,
    "high": Colors.RED,
    "medium": Colors.YELLOW,
    "low": Colors.GREEN,
}

# Category icons
CATEGORY_ICONS = {
    "syntax": "📝",
    "runtime": "💥",
    "logic": "🧩",
    "dependency": "📦",
    "config": "⚙️",
    "memory": "🧠",
    "network": "🌐",
}

SEVERITY_ICONS = {
    "critical": "🔴",
    "high": "🟠",
    "medium": "🟡",
    "low": "🟢",
}


class OutputFormatter:
    """Formats analysis results for terminal and JSON output."""

    def __init__(self, use_colors: bool = True):
        """
        Initialize the formatter.

        Args:
            use_colors: Whether to use ANSI colors in output.
        """
        self.use_colors = use_colors
        if not use_colors:
            Colors.disable()

    def format_human(self, result: dict, index: Optional[int] = None) -> str:
        """
        Format analysis result as human-readable terminal output.

        Args:
            result: The analysis result dict.
            index: Optional batch index.

        Returns:
            Formatted string.
        """
        lines = []
        border = f"{Colors.DIM}{'─' * 70}{Colors.RESET}"

        # Header
        header = f"{Colors.BOLD}{'═' * 70}{Colors.RESET}"
        lines.append(header)
        if index is not None:
            lines.append(f"{Colors.BOLD} Error #{index + 1}{Colors.RESET}")
        lines.append(header)

        # Detection info
        det = result.get("detection", {})
        cat = result.get("categorization", {})
        severity = cat.get("severity", "unknown")
        sev_color = SEVERITY_COLORS.get(severity, Colors.RESET)
        sev_icon = SEVERITY_ICONS.get(severity, "")
        cat_icon = CATEGORY_ICONS.get(cat.get("category", ""), "")

        lines.append(
            f"  {Colors.CYAN}Language:{Colors.RESET} {det.get('language', 'Unknown')}"
            f" ({det.get('framework', 'N/A')})  "
            f"{Colors.DIM}[confidence: {det.get('confidence', 0)}%]{Colors.RESET}"
        )
        lines.append(
            f"  {Colors.CYAN}Category:{Colors.RESET} {cat_icon} {cat.get('category', 'unknown').upper()}"
            f"  |  {Colors.CYAN}Severity:{Colors.RESET} {sev_icon} {sev_color}{severity.upper()}{Colors.RESET}"
            f"  {Colors.DIM}[confidence: {cat.get('confidence', 0)}%]{Colors.RESET}"
        )

        error_type = result.get("error_type")
        if error_type:
            lines.append(f"  {Colors.CYAN}Error Type:{Colors.RESET} {error_type[:100]}")

        # File references
        file_refs = result.get("file_references", [])
        if file_refs:
            lines.append(f"\n  {Colors.CYAN}File References:{Colors.RESET}")
            for ref in file_refs[:5]:
                line_info = f":{ref['line']}" if ref.get("line") else ""
                lines.append(f"    {Colors.DIM}→{Colors.RESET} {ref['file']}{line_info}")

        # AI Analysis
        ai = result.get("ai_analysis", {})
        if ai:
            lines.append(border)
            lines.append(f"  {Colors.BOLD}🤖 AI Analysis{Colors.RESET}")
            lines.append(border)

            if ai.get("summary"):
                lines.append(f"\n  {Colors.BOLD}Summary:{Colors.RESET}")
                lines.append(f"    {ai['summary']}")

            if ai.get("root_cause"):
                lines.append(f"\n  {Colors.BOLD}Root Cause:{Colors.RESET}")
                lines.append(f"    {ai['root_cause']}")

            if ai.get("solution"):
                lines.append(f"\n  {Colors.BOLD}Solution:{Colors.RESET}")
                lines.append(f"    {ai['solution']}")

            if ai.get("code_example"):
                lines.append(f"\n  {Colors.BOLD}Code Fix:{Colors.RESET}")
                lines.append(f"  {Colors.DIM}{'-' * 50}{Colors.RESET}")
                for code_line in ai["code_example"].split("\n"):
                    lines.append(f"  {Colors.GREEN}{code_line}{Colors.RESET}")
                lines.append(f"  {Colors.DIM}{'-' * 50}{Colors.RESET}")

            if ai.get("prevention"):
                lines.append(f"\n  {Colors.BOLD}Prevention:{Colors.RESET}")
                lines.append(f"    {ai['prevention']}")

            if ai.get("related_errors"):
                lines.append(f"\n  {Colors.BOLD}Related Issues:{Colors.RESET}")
                for rel in ai["related_errors"]:
                    lines.append(f"    {Colors.YELLOW}•{Colors.RESET} {rel}")

        # Suggestions
        suggestions = result.get("suggestions", [])
        if suggestions:
            lines.append(border)
            lines.append(f"  {Colors.BOLD}💡 Quick Fix Suggestions{Colors.RESET}")
            lines.append(border)
            for suggestion in suggestions:
                lines.append(f"    {Colors.GREEN}•{Colors.RESET} {suggestion}")

        lines.append(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}\n")
        return "\n".join(lines)

    def format_json(self, result: dict, index: Optional[int] = None) -> str:
        """
        Format analysis result as JSON.

        Args:
            result: The analysis result dict.
            index: Optional batch index.

        Returns:
            JSON string.
        """
        output = dict(result)
        if index is not None:
            output["batch_index"] = index
        return json.dumps(output, indent=2, ensure_ascii=False, default=str)

    def format_batch_json(self, results: list) -> str:
        """
        Format batch results as a JSON array with summary.

        Args:
            results: List of analysis result dicts.

        Returns:
            JSON string.
        """
        output = {
            "total_errors": len(results),
            "summary": self._generate_summary(results),
            "errors": results,
        }
        return json.dumps(output, indent=2, ensure_ascii=False, default=str)

    def _generate_summary(self, results: list) -> dict:
        """Generate a summary across multiple errors."""
        languages = {}
        categories = {}
        severities = {}

        for result in results:
            lang = result.get("detection", {}).get("language", "Unknown")
            cat = result.get("categorization", {}).get("category", "unknown")
            sev = result.get("categorization", {}).get("severity", "unknown")

            languages[lang] = languages.get(lang, 0) + 1
            categories[cat] = categories.get(cat, 0) + 1
            severities[sev] = severities.get(sev, 0) + 1

        return {
            "languages": languages,
            "categories": categories,
            "severities": severities,
            "highest_severity": self._highest_severity(results),
        }

    def _highest_severity(self, results: list) -> str:
        """Find the highest severity across all results."""
        severity_order = ["low", "medium", "high", "critical"]
        highest = 0

        for result in results:
            sev = result.get("categorization", {}).get("severity", "low")
            if sev in severity_order:
                idx = severity_order.index(sev)
                if idx > highest:
                    highest = idx

        return severity_order[highest] if severity_order[highest] else "unknown"
