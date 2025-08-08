"""Tests for submission module."""

import unittest
from unittest.mock import Mock, patch, MagicMock
import tempfile
import os
from pathlib import Path

from leetcode_cli.submission import SubmissionManager


class TestSubmissionManager(unittest.TestCase):
    """Test cases for SubmissionManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.submission_manager = SubmissionManager()
    
    @patch('leetcode_cli.submission.AuthManager')
    def test_init(self, mock_auth):
        """Test SubmissionManager initialization."""
        manager = SubmissionManager()
        self.assertIsNotNone(manager.auth)
        self.assertIsNotNone(manager.cache)
        self.assertIsNotNone(manager.session)
    
    def test_read_solution_file(self):
        """Test reading solution file."""
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp.write('def solution():\n    return "Hello World"')
            tmp_path = tmp.name
        
        try:
            content = self.submission_manager._read_solution_file(tmp_path)
            self.assertIn('def solution()', content)
            self.assertIn('Hello World', content)
        finally:
            os.unlink(tmp_path)
    
    def test_read_solution_file_not_found(self):
        """Test reading non-existent solution file."""
        with self.assertRaises(Exception) as context:
            self.submission_manager._read_solution_file('non_existent_file.py')
        
        self.assertIn('Solution file not found', str(context.exception))
    
    def test_get_language_slug(self):
        """Test language slug conversion."""
        test_cases = [
            ('python', 'python3'),
            ('python3', 'python3'),
            ('java', 'java'),
            ('cpp', 'cpp'),
            ('c++', 'cpp'),
            ('javascript', 'javascript'),
            ('go', 'golang'),
            ('unknown', 'unknown')
        ]
        
        for input_lang, expected in test_cases:
            result = self.submission_manager._get_language_slug(input_lang)
            self.assertEqual(result, expected, f"Failed for language: {input_lang}")
    
    def test_filter_submissions(self):
        """Test submission filtering."""
        submissions = [
            {
                'title_slug': 'two-sum',
                'status_display': 'Accepted',
                'lang': 'python3'
            },
            {
                'title_slug': 'add-two-numbers',
                'status_display': 'Wrong Answer',
                'lang': 'java'
            },
            {
                'title_slug': 'two-sum',
                'status_display': 'Accepted',
                'lang': 'java'
            }
        ]
        
        # Filter by problem
        filtered = self.submission_manager._filter_submissions(
            submissions, problem_slug='two-sum'
        )
        self.assertEqual(len(filtered), 2)
        
        # Filter by status
        filtered = self.submission_manager._filter_submissions(
            submissions, status='accepted'
        )
        self.assertEqual(len(filtered), 2)
        
        # Filter by language
        filtered = self.submission_manager._filter_submissions(
            submissions, language='java'
        )
        self.assertEqual(len(filtered), 2)
        
        # Multiple filters
        filtered = self.submission_manager._filter_submissions(
            submissions, problem_slug='two-sum', language='java'
        )
        self.assertEqual(len(filtered), 1)
    
    @patch('leetcode_cli.submission.AuthManager')
    def test_submit_solution_not_authenticated(self, mock_auth):
        """Test submission when not authenticated."""
        mock_auth_instance = Mock()
        mock_auth_instance.is_authenticated.return_value = False
        mock_auth.return_value = mock_auth_instance
        
        manager = SubmissionManager()
        
        with self.assertRaises(Exception) as context:
            manager.submit_solution('two-sum', 'solution.py', 'python3')
        
        self.assertIn('Not authenticated', str(context.exception))
    
    @patch('leetcode_cli.submission.AuthManager')
    def test_run_test_cases_not_authenticated(self, mock_auth):
        """Test running test cases when not authenticated."""
        mock_auth_instance = Mock()
        mock_auth_instance.is_authenticated.return_value = False
        mock_auth.return_value = mock_auth_instance
        
        manager = SubmissionManager()
        
        with self.assertRaises(Exception) as context:
            manager.run_test_cases('two-sum', 'solution.py', 'python3')
        
        self.assertIn('Not authenticated', str(context.exception))


if __name__ == '__main__':
    unittest.main()
