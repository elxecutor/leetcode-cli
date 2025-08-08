"""Test configuration and fixtures."""

import pytest
from unittest.mock import Mock, patch

from leetcode_cli.auth import AuthManager
from leetcode_cli.profile import ProfileManager
from leetcode_cli.problem import ProblemManager


@pytest.fixture
def mock_auth_manager():
    """Mock AuthManager for testing."""
    with patch('leetcode_cli.auth.AuthManager') as mock:
        mock_instance = Mock()
        mock_instance.is_authenticated.return_value = True
        mock_instance.get_session.return_value = Mock()
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_user_profile():
    """Sample user profile data for testing."""
    return {
        'username': 'testuser',
        'profile': {
            'realName': 'Test User',
            'company': 'Test Company',
            'school': 'Test University',
            'countryName': 'Test Country'
        },
        'stats': {
            'total_solved': 100,
            'total_submissions': 200,
            'acceptance_rate': 50.0,
            'difficulty_breakdown': {
                'Easy': {'solved': 50, 'total': 80, 'acceptance_rate': 62.5},
                'Medium': {'solved': 40, 'total': 90, 'acceptance_rate': 44.4},
                'Hard': {'solved': 10, 'total': 30, 'acceptance_rate': 33.3}
            }
        },
        'badges': [],
        'contest_ranking': None,
        'avatar_url': None
    }


@pytest.fixture
def sample_problem():
    """Sample problem data for testing."""
    return {
        'id': '1',
        'title': 'Two Sum',
        'title_slug': 'two-sum',
        'difficulty': 'Easy',
        'acceptance_rate': 49.5,
        'is_paid_only': False,
        'status': None,
        'tags': ['Array', 'Hash Table']
    }
