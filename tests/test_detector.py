"""
Tests for the LanguageDetector module.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from lib.detector import LanguageDetector


class TestLanguageDetector:
    """Test cases for language detection."""

    def setup_method(self):
        self.detector = LanguageDetector()

    def test_detect_python_traceback(self):
        text = """Traceback (most recent call last):
  File "/app/main.py", line 10, in <module>
    x = y + 1
NameError: name 'y' is not defined"""
        result = self.detector.detect(text)
        assert result["language"] == "Python", f"Expected Python, got {result['language']}"
        assert result["confidence"] > 0.0
        assert result["file_extension"] == ".py"

    def test_detect_nodejs_error(self):
        text = """TypeError: Cannot read properties of undefined (reading 'map')
    at processItems (/app/src/utils.js:42:12)
    at /app/node_modules/express/lib/router.js:470:5"""
        result = self.detector.detect(text)
        assert result["language"] == "Node.js", f"Expected Node.js, got {result['language']}"
        assert result["confidence"] > 0.0

    def test_detect_java_exception(self):
        text = """java.lang.NullPointerException: Cannot invoke method on null
    at com.app.Service.process(Service.java:45)
Caused by: java.io.IOException: Connection refused"""
        result = self.detector.detect(text)
        assert result["language"] == "Java", f"Expected Java, got {result['language']}"
        assert result["confidence"] > 0.0

    def test_detect_go_panic(self):
        text = """goroutine 1 [running]:
main.main()
	/app/main.go:10 +0x20

panic: runtime error: nil pointer dereference"""
        result = self.detector.detect(text)
        assert result["language"] == "Go", f"Expected Go, got {result['language']}"
        assert result["confidence"] > 0.0

    def test_detect_rust_error(self):
        text = """error[E0507]: cannot move out of `user`
  --> src/main.rs:15:5
   |
15 |     process_user(user);
   |                    ^^^^ move occurs because `user` has type `User`, which does not implement the `Copy` trait"""
        result = self.detector.detect(text)
        assert result["language"] == "Rust", f"Expected Rust, got {result['language']}"
        assert result["confidence"] > 0.0

    def test_detect_csharp_exception(self):
        text = """Unhandled exception. System.NullReferenceException: Object reference not set to an instance of an object.
   at MyApp.Service.GetData(Service.cs:line 23)"""
        result = self.detector.detect(text)
        assert result["language"] == "C#", f"Expected C#, got {result['language']}"
        assert result["confidence"] > 0.0

    def test_detect_ruby_error(self):
        text = """app/services/user_service.rb:42:in `find': undefined method `name' for nil:NilClass (NoMethodError)
	from app/controllers/users_controller.rb:15:in `index'"""
        result = self.detector.detect(text)
        assert result["language"] == "Ruby", f"Expected Ruby, got {result['language']}"
        assert result["confidence"] > 0.0

    def test_detect_php_fatal(self):
        text = """Fatal error: Uncaught Error: Call to undefined function app\\connect() in /var/www/html/src/Database.php:34
Stack trace:
#0 /var/www/html/public/index.php(10): Database->init()
  thrown in /var/www/html/src/Database.php on line 34"""
        result = self.detector.detect(text)
        assert result["language"] == "PHP", f"Expected PHP, got {result['language']}"
        assert result["confidence"] > 0.0

    def test_detect_unknown(self):
        text = "This is just plain text with no error patterns."
        result = self.detector.detect(text)
        assert result["language"] == "Unknown"
        assert result["confidence"] == 0.0

    def test_extract_error_type(self):
        text = 'NameError: name "undefined_var" is not defined'
        error_type = self.detector.extract_error_type(text, "Python")
        assert error_type is not None
        assert "NameError" in error_type

    def test_extract_file_references(self):
        text = """Traceback (most recent call last):
  File "/app/src/main.py", line 10, in <module>
    import missing_module
ModuleNotFoundError: No module named 'missing_module'"""
        refs = self.detector.extract_file_references(text)
        assert len(refs) >= 1
        assert any("/app/src/main.py" in r["file"] for r in refs)

    def test_detect_django_framework(self):
        text = """Traceback (most recent call last):
  File "/app/manage.py", line 22, in <module>
  File "django/core/management/__init__.py", line 384
django.core.exceptions.AppRegistryNotReady: Apps aren't loaded yet."""
        result = self.detector.detect(text)
        assert result["language"] == "Python"
        assert result["framework"] == "Django"

    def test_detect_express_framework(self):
        text = """TypeError: Cannot read properties of undefined
    at Layer.handle (/app/node_modules/express/lib/router/layer.js:95:5)
    at /app/node_modules/express/lib/router.js:470:5"""
        result = self.detector.detect(text)
        assert result["language"] == "Node.js"
        assert result["framework"] == "Express.js"

    def test_rich_python_traceback(self):
        """Test with a more complete Python traceback for higher confidence."""
        text = """Traceback (most recent call last):
  File "/app/src/main.py", line 15, in <module>
    from utils.database import get_connection
  File "/app/src/utils/database.py", line 8, in <module>
    from sqlalchemy import create_engine
ModuleNotFoundError: No module named 'sqlalchemy'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/app/src/main.py", line 15, in <module>
    raise ImportError("Database module required")
ImportError: Database module required"""
        result = self.detector.detect(text)
        assert result["language"] == "Python"
        assert result["confidence"] >= 0.3


def run_tests():
    """Simple test runner."""
    test = TestLanguageDetector()
    test.setup_method()
    tests = [m for m in dir(test) if m.startswith("test_")]
    passed = 0
    failed = 0

    for test_name in tests:
        test.setup_method()
        try:
            getattr(test, test_name)()
            print(f"  ✅ {test_name}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {test_name}: {e}")
            failed += 1

    print(f"\nResults: {passed} passed, {failed} failed, {passed + failed} total")
    return failed == 0


if __name__ == "__main__":
    print("Running detector tests...\n")
    success = run_tests()
    sys.exit(0 if success else 1)
