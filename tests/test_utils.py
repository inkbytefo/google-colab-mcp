"""Tests for utility functions."""

import json
import tempfile
import unittest
from unittest.mock import patch, Mock

from src.utils import (
    load_config,
    validate_notebook_id,
    sanitize_filename,
    create_notebook_content,
    create_code_cell,
    create_text_cell,
    extract_error_message,
    is_valid_python_code,
    format_execution_time,
    retry_with_backoff
)


class TestUtils(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_load_config_valid_file(self):
        """Test loading valid configuration file."""
        config_data = {
            "server": {"host": "localhost", "port": 8080},
            "logging": {"level": "INFO"}
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_file = f.name
        
        try:
            result = load_config(config_file)
            self.assertEqual(result, config_data)
        finally:
            import os
            os.unlink(config_file)
    
    def test_load_config_missing_file(self):
        """Test loading missing configuration file."""
        result = load_config("nonexistent.json")
        self.assertEqual(result, {})
    
    def test_load_config_invalid_json(self):
        """Test loading invalid JSON file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("invalid json content")
            config_file = f.name
        
        try:
            result = load_config(config_file)
            self.assertEqual(result, {})
        finally:
            import os
            os.unlink(config_file)
    
    def test_validate_notebook_id_valid(self):
        """Test validation of valid notebook IDs."""
        valid_ids = [
            "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms",
            "1ABC123DEF456GHI789JKL012MNO345PQR678STU901VWX234YZ567",
            "abc123-def456_ghi789"
        ]
        
        for notebook_id in valid_ids:
            with self.subTest(notebook_id=notebook_id):
                self.assertTrue(validate_notebook_id(notebook_id))
    
    def test_validate_notebook_id_invalid(self):
        """Test validation of invalid notebook IDs."""
        invalid_ids = [
            "",
            None,
            "too_short",
            "contains/invalid/characters",
            "contains spaces",
            "a" * 100  # too long
        ]
        
        for notebook_id in invalid_ids:
            with self.subTest(notebook_id=notebook_id):
                self.assertFalse(validate_notebook_id(notebook_id))
    
    def test_sanitize_filename(self):
        """Test filename sanitization."""
        test_cases = [
            ("normal_file.txt", "normal_file.txt"),
            ("file with spaces.txt", "file with spaces.txt"),
            ("file<>:\"/\\|?*.txt", "file_________.txt"),
            ("  .hidden_file  ", "hidden_file"),
            ("", "untitled"),
            ("   ", "untitled"),
            ("...", "untitled")
        ]
        
        for input_name, expected in test_cases:
            with self.subTest(input_name=input_name):
                result = sanitize_filename(input_name)
                self.assertEqual(result, expected)
    
    def test_create_notebook_content(self):
        """Test notebook content creation."""
        # Test with no cells
        content = create_notebook_content()
        self.assertEqual(content["nbformat"], 4)
        self.assertEqual(content["nbformat_minor"], 0)
        self.assertIn("metadata", content)
        self.assertEqual(content["cells"], [])
        
        # Test with cells
        cells = [create_code_cell("print('hello')")]
        content = create_notebook_content(cells)
        self.assertEqual(len(content["cells"]), 1)
        self.assertEqual(content["cells"][0]["cell_type"], "code")
    
    def test_create_code_cell(self):
        """Test code cell creation."""
        source = "print('hello')\nprint('world')"
        cell = create_code_cell(source)
        
        self.assertEqual(cell["cell_type"], "code")
        self.assertEqual(cell["source"], ["print('hello')", "print('world')"])
        self.assertEqual(cell["execution_count"], None)
        self.assertEqual(cell["outputs"], [])
        
        # Test with list source
        source_list = ["print('hello')", "print('world')"]
        cell = create_code_cell(source_list)
        self.assertEqual(cell["source"], source_list)
    
    def test_create_text_cell(self):
        """Test text cell creation."""
        source = "# Header\nSome text"
        
        # Test markdown cell (default)
        cell = create_text_cell(source)
        self.assertEqual(cell["cell_type"], "markdown")
        self.assertEqual(cell["source"], ["# Header", "Some text"])
        
        # Test raw cell
        cell = create_text_cell(source, "raw")
        self.assertEqual(cell["cell_type"], "raw")
    
    def test_extract_error_message(self):
        """Test error message extraction."""
        test_cases = [
            (Exception("Simple error"), "Simple error"),
            (Exception("Message: Prefixed error"), "Prefixed error"),
            (Exception("selenium.common.exceptions.TimeoutException: Timeout"), "TimeoutException: Timeout"),
            (Exception("googleapiclient.errors.HttpError: 404 Not Found"), "HttpError: 404 Not Found")
        ]
        
        for error, expected in test_cases:
            with self.subTest(error=str(error)):
                result = extract_error_message(error)
                self.assertEqual(result, expected)
    
    def test_is_valid_python_code(self):
        """Test Python code validation."""
        valid_code = [
            "print('hello')",
            "x = 1\ny = 2\nprint(x + y)",
            "def func():\n    return 42",
            "import os\nprint(os.getcwd())"
        ]
        
        invalid_code = [
            "print('unclosed string",
            "def func(\n    pass",
            "if True\n    print('missing colon')",
            "import"
        ]
        
        for code in valid_code:
            with self.subTest(code=code):
                self.assertTrue(is_valid_python_code(code))
        
        for code in invalid_code:
            with self.subTest(code=code):
                self.assertFalse(is_valid_python_code(code))
    
    def test_format_execution_time(self):
        """Test execution time formatting."""
        test_cases = [
            (0.001, "1ms"),
            (0.5, "500ms"),
            (1.0, "1.0s"),
            (1.234, "1.2s"),
            (59.9, "59.9s"),
            (60.0, "1m 0.0s"),
            (65.5, "1m 5.5s"),
            (125.7, "2m 5.7s")
        ]
        
        for seconds, expected in test_cases:
            with self.subTest(seconds=seconds):
                result = format_execution_time(seconds)
                self.assertEqual(result, expected)
    
    def test_retry_with_backoff_success(self):
        """Test retry decorator with successful function."""
        @retry_with_backoff(max_retries=3, delay=0.1)
        def successful_function():
            return "success"
        
        result = successful_function()
        self.assertEqual(result, "success")
    
    def test_retry_with_backoff_eventual_success(self):
        """Test retry decorator with function that succeeds after retries."""
        call_count = 0
        
        @retry_with_backoff(max_retries=3, delay=0.1)
        def eventually_successful_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = eventually_successful_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 3)
    
    def test_retry_with_backoff_max_retries_exceeded(self):
        """Test retry decorator when max retries are exceeded."""
        @retry_with_backoff(max_retries=2, delay=0.1)
        def always_failing_function():
            raise Exception("Always fails")
        
        with self.assertRaises(Exception):
            always_failing_function()


if __name__ == '__main__':
    unittest.main()