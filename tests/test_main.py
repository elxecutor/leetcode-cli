"""Tests for the main CLI application."""

import pytest
from typer.testing import CliRunner
from unittest.mock import patch, Mock

from leetcode_cli.main import app


runner = CliRunner()


def test_profile_command_json_output():
    """Test profile command with JSON output."""
    mock_profile_data = {
        'username': 'testuser',
        'stats': {'total_solved': 100}
    }
    
    with patch('leetcode_cli.main.ProfileManager') as mock_profile_manager:
        mock_instance = Mock()
        mock_instance.get_user_profile.return_value = mock_profile_data
        mock_profile_manager.return_value = mock_instance
        
        result = runner.invoke(app, ["profile", "testuser", "--json"])
        assert result.exit_code == 0
        assert "testuser" in result.stdout


def test_daily_command():
    """Test daily challenge command."""
    mock_daily_data = {
        'date': '2024-01-01',
        'problem': {
            'id': '1',
            'title': 'Test Problem',
            'difficulty': 'Easy'
        }
    }
    
    with patch('leetcode_cli.main.ProblemManager') as mock_problem_manager:
        mock_instance = Mock()
        mock_instance.get_daily_challenge.return_value = mock_daily_data
        mock_problem_manager.return_value = mock_instance
        
        result = runner.invoke(app, ["daily"])
        assert result.exit_code == 0


def test_search_command():
    """Test search command."""
    mock_problems = [
        {
            'id': '1',
            'title': 'Two Sum',
            'difficulty': 'Easy',
            'acceptance_rate': 49.5
        }
    ]
    
    with patch('leetcode_cli.main.ProblemManager') as mock_problem_manager:
        mock_instance = Mock()
        mock_instance.search_problems.return_value = mock_problems
        mock_problem_manager.return_value = mock_instance
        
        result = runner.invoke(app, ["search", "two sum"])
        assert result.exit_code == 0


def test_problem_command():
    """Test problem details command."""
    mock_problem_data = {
        'id': '1',
        'title': 'Two Sum',
        'difficulty': 'Easy',
        'content': '<p>Test problem content</p>'
    }
    
    with patch('leetcode_cli.main.ProblemManager') as mock_problem_manager:
        mock_instance = Mock()
        mock_instance.get_problem_details.return_value = mock_problem_data
        mock_problem_manager.return_value = mock_instance
        
        result = runner.invoke(app, ["problem", "1"])
        assert result.exit_code == 0
