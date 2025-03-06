'''
This tests the input validation functionality of the code review assistant.
It ensures that the system can correctly identify and handle non-code inputs.

How to run:
pytest test_input_validation.py

'''

import pytest
import os
import sys
import unittest.mock as mock
import tempfile
from datetime import datetime

# Add the parent directory to the Python path to import the module for testing
#sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import functions to be tested - adjust import based on actual module structure
from code_review_assitant import (
    format_assistant_response,
    save_code_review,
    query_assistant,
    review_code,
)

class TestInputValidation:
    """Test cases for validating input to ensure only code is processed."""
    
    def test_non_code_detection(self):
        """Test that the system can detect when input is not code."""
        with mock.patch('interpreter.interpreter.chat') as mock_chat:
            # Setup mock to return a response that shows rejection of non-code input
            mock_chat.return_value = {
                "content": "I can only review code. Please submit actual programming code for review."
            }
            
            test_input = "This is just a regular sentence, not code."
            response = query_assistant(f"Please review this: {test_input}")
            assert "I can only review code" in format_assistant_response(response)
            
    def test_code_acceptance(self):
        """Test that the system accepts and processes valid code."""
        with mock.patch('interpreter.interpreter.chat') as mock_chat:
            mock_chat.return_value = {
                "content": "Here's my review of your code..."
            }
            
            test_input = """
def hello_world():
    print("Hello, world!")
"""
            response = query_assistant(f"Please review this code: {test_input}")
            assert "I can only review code" not in format_assistant_response(response)

    def test_mixed_content_detection(self):
        """Test how the system handles input with both code and extensive natural language."""
        with mock.patch('interpreter.interpreter.chat') as mock_chat:
            mock_chat.return_value = {
                "content": "Here's my review of the code portion..."
            }
            
            test_input = """
Here's a lengthy explanation about what I'm trying to do.
I'm working on a project that needs to calculate some values.
Maybe you can help me with this function:

def calculate_area(radius):
    return 3.14 * radius * radius

What do you think about this code? Is it good?
"""
            response = query_assistant(f"Please review this: {test_input}")
            assert mock_chat.called
            assert "review of the code" in format_assistant_response(response)

    def test_format_assistant_response_dict(self):
        """Test that format_assistant_response correctly handles dictionary responses."""
        test_response = {"content": "This is the formatted content"}
        formatted = format_assistant_response(test_response)
        assert formatted == "This is the formatted content"
        
    def test_format_assistant_response_list(self):
        """Test that format_assistant_response correctly handles list responses."""
        test_response = [
            {"content": "Part 1"}, 
            {"content": "Part 2"}
        ]
        formatted = format_assistant_response(test_response)
        assert formatted == "Part 1\nPart 2"
        
    def test_format_assistant_response_string(self):
        """Test that format_assistant_response correctly handles string responses."""
        test_response = "Direct string response"
        formatted = format_assistant_response(test_response)
        assert formatted == "Direct string response"
        
    @mock.patch('os.environ.get', return_value='test_reviews')
    @mock.patch('os.makedirs')
    @mock.patch('builtins.open', new_callable=mock.mock_open)
    def test_save_code_review(self, mock_open, mock_makedirs, _):
        """Test that code reviews are saved correctly."""
        fixed_datetime = datetime(2023, 1, 1, 12, 0, 0)
        with mock.patch('code_review_assitant.datetime') as mock_dt:
            mock_dt.now.return_value = fixed_datetime
            
            original_code = "def test(): pass"
            assistant_response = {"content": "Good code!"}
            
            result_filepath = save_code_review(original_code, assistant_response)
            assert result_filepath == os.path.join('test_reviews', 'code_review_20230101_120000.md')
        
        mock_makedirs.assert_called_once_with('test_reviews', exist_ok=True)
        expected_path = os.path.join('test_reviews', 'code_review_20230101_120000.md')
        mock_open.assert_called_once_with(expected_path, 'w', encoding='utf-8')
        
        mock_file = mock_open()
        write_calls = mock_file.write.call_args_list
        content = ''.join(call.args[0] for call in write_calls)
        
        assert "# Code Review" in content
        assert "## Original Code" in content
        assert "```python" in content
        assert original_code in content
        assert "Good code!" in content
        
    @mock.patch('interpreter.interpreter.chat')
    def test_review_code_function(self, mock_chat):
        """Test the review_code function with mocked interpreter."""
        with mock.patch('code_review_assitant.save_code_review', return_value='/path/to/review.md'):
            mock_chat.return_value = {"content": "Code review content"}
            test_code = "print('hello world')"
            response = review_code(test_code)
            mock_chat.assert_called_once()
            call_args = mock_chat.call_args[0][0]
            assert test_code in call_args
            assert "suggest improvements" in call_args
            assert format_assistant_response(response) == "Code review content"
            
        with mock.patch('interpreter.interpreter.chat') as mock_chat_2:
            mock_chat_2.return_value = {
                "content": "I can only review code. Please submit actual programming code for review."
            }
            
            test_input = "This is just a regular sentence, not code."
            from code_review_assitant import query_assistant
            response = query_assistant(f"Please review this: {test_input}")
            assert "I can only review code" in format_assistant_response(response)
