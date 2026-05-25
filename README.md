# 🕵️ Error Analyzer Agent

[![Python 3.9+](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/error-analyzer-agent/error-analyzer-agent)

AI-powered error log and stack trace analyzer that uses MiMo API to provide intelligent debugging assistance. Supports 8 programming languages with automatic detection, error categorization, severity assessment, and solution generation.

## ✨ Features

- 🌐 **Multi-language support**: Python, Node.js, Java, Go, Rust, C#, Ruby, PHP
- 🔍 **Auto-detection**: Automatically identifies language and framework from stack traces
- 📊 **Error categorization**: Syntax, Runtime, Logic, Dependency, Config, Memory, Network
- ⚠️ **Severity assessment**: Critical, High, Medium, Low with context-aware escalation
- 🤖 **AI-powered analysis**: Root cause analysis, solutions, and code examples via MiMo API
- 📦 **Batch analysis**: Analyze multiple errors in one file
- 📄 **Dual output**: Human-readable terminal + machine-readable JSON
- 🧪 **CLI tool**: Full command-line interface with flexible options

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/error-analyzer-agent/error-analyzer-agent.git
cd error-analyzer-agent

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .
```

### Prerequisites

- Python 3.9+
- MiMo API running (default: `http://localhost:20128/v1`)

## 📖 Usage

### Basic Usage

```bash
# Analyze a stack trace file
python analyzer.py examples/python_error.txt

# Analyze with JSON output
python analyzer.py --json examples/python_error.txt

# Pipe from another command
cat error.log | python analyzer.py --stdin
```

### Batch Analysis

```bash
# Analyze multiple errors in one file
python analyzer.py --batch errors.log

# Batch with JSON output
python analyzer.py --batch --json errors.log
```

### Language Detection Only

```bash
# Just detect the language (no AI analysis)
python analyzer.py --detect examples/java_error.txt
```

### Advanced Options

```bash
# Override language detection
python analyzer.py --lang python error.log

# Custom API endpoint
python analyzer.py --api-base http://my-server:8080/v1 error.log

# Disable colors (useful for piping)
python analyzer.py --no-color error.log
```

## 📁 Project Structure

```
error-analyzer-agent/
├── analyzer.py          # Main CLI tool
├── lib/
│   ├── __init__.py      # Package init
│   ├── detector.py      # Language/framework detection
│   ├── categorizer.py   # Error categorization & severity
│   ├── analyzer.py      # Core analysis engine
│   └── formatter.py     # Output formatting (text/JSON)
├── examples/
│   ├── python_error.txt
│   ├── nodejs_error.txt
│   ├── java_error.txt
│   ├── go_error.txt
│   ├── rust_error.txt
│   └── csharp_error.txt
├── tests/
│   └── test_detector.py
├── README.md
├── requirements.txt
├── setup.py
└── LICENSE
```

## 🔧 Configuration

### API Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `--api-base` | `http://localhost:20128/v1` | MiMo API base URL |
| `--model` | `mimo-v2.5-pro` | Model name to use |

### Environment Variables

```bash
# Override defaults (optional)
export MIMO_API_BASE="http://localhost:20128/v1"
export MIMO_MODEL="mimo-v2.5-pro"
```

## 📊 Output Example

### Human-Readable Output

```
════════════════════════════════════════════════════════════════════════
 Error #1
════════════════════════════════════════════════════════════════════════
  Language: Python (Flask)  [confidence: 0.95%]
  Category: 📦 DEPENDENCY  |  Severity: 🟡 MEDIUM  [confidence: 0.89%]
  Error Type: ModuleNotFoundError: No module named 'sqlalchemy'

  File References:
    → /app/src/main.py:15

──────────────────────────────────────────────────────────────────────────
  🤖 AI Analysis
──────────────────────────────────────────────────────────────────────────

  Summary:
    Python cannot find the 'sqlalchemy' module because it's not installed.

  Root Cause:
    The SQLAlchemy ORM package is not installed in the Python environment.

  Solution:
    Install the missing dependency with pip:
    pip install sqlalchemy

  Code Fix:
    ──────────────────────────────────────────────────────────────────
    # Run this command to install the missing dependency:
    pip install sqlalchemy

    # Or add to requirements.txt:
    echo "sqlalchemy>=2.0.0" >> requirements.txt
    ──────────────────────────────────────────────────────────────────

  Prevention:
    - Always include dependencies in requirements.txt
    - Use virtual environments to manage dependencies
    - Run `pip install -r requirements.txt` after cloning
════════════════════════════════════════════════════════════════════════
```

### JSON Output

```json
{
  "error_text": "Traceback (most recent call last):\n...",
  "detection": {
    "language": "Python",
    "framework": "Flask",
    "confidence": 0.95,
    "file_extension": ".py"
  },
  "error_type": "ModuleNotFoundError: No module named 'sqlalchemy'",
  "categorization": {
    "category": "dependency",
    "severity": "medium",
    "confidence": 0.89
  },
  "file_references": [
    {"file": "/app/src/main.py", "line": "15"}
  ],
  "ai_analysis": {
    "summary": "Missing SQLAlchemy dependency",
    "root_cause": "The SQLAlchemy ORM package is not installed.",
    "solution": "Install with: pip install sqlalchemy",
    "code_example": "pip install sqlalchemy",
    "prevention": "Use requirements.txt for dependency management",
    "related_errors": []
  },
  "suggestions": [
    "Check if the package/module is installed",
    "Verify package version compatibility",
    "Run: pip install -r requirements.txt"
  ]
}
```

## 🧪 Testing

```bash
# Run the detector tests
python tests/test_detector.py

# Or use pytest
pip install pytest
pytest tests/
```

## 📚 Error Categories

| Category | Description | Examples |
|----------|-------------|----------|
| **syntax** | Parse/syntax errors | SyntaxError, ParseError, IndentationError |
| **runtime** | Runtime exceptions | TypeError, ValueError, NullReferenceException |
| **logic** | Logic/algorithm errors | AssertionError, infinite loops, deadlocks |
| **dependency** | Missing/incompatible deps | ImportError, MODULE_NOT_FOUND, ClassNotFoundException |
| **config** | Configuration/environment | PermissionError, FileNotFoundError, config errors |
| **memory** | Memory-related | MemoryError, OutOfMemoryError, SegmentationFault |
| **network** | Network/connectivity | ConnectionError, TimeoutError, SSL errors |

## 🌐 Supported Languages

| Language | Error Patterns | Framework Detection |
|----------|----------------|---------------------|
| Python | Traceback, .py files | Django, Flask, FastAPI, Pydantic |
| Node.js | .js/.ts stack traces | Express, React, Next.js, NestJS |
| Java | java.*Exception | Spring, Hibernate, Android |
| Go | goroutine, panic | Gin, Echo, Fiber, GORM |
| Rust | error[E*], .rs files | Actix, Tokio, Serde |
| C# | System.*Exception | ASP.NET, Entity Framework |
| Ruby | .rb/.erb files | Rails, Sinatra, Sidekiq |
| PHP | Fatal error, .php files | Laravel, Symfony, WordPress |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [MiMo](https://github.com/mimo-ai/mimo) for the powerful AI model
- [OpenAI Python SDK](https://github.com/openai/openai-python) for the client library
- The open-source community for inspiration and best practices
