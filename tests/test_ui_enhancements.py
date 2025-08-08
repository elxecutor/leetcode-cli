"""Tests for UI manager enhancements."""

import unittest
from unittest.mock import Mock, patch
from io import StringIO

from leetcode_cli.ui import UIManager
from rich.console import Console


class TestUIManagerEnhancements(unittest.TestCase):
    """Test cases for enhanced UI manager functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.console = Console(file=StringIO(), force_terminal=True)
        self.ui_manager = UIManager(self.console)
    
    def test_display_submission_result_accepted(self):
        """Test displaying accepted submission result."""
        result = {
            'status': 'completed',
            'status_code': 10,  # Accepted
            'status_msg': 'Accepted',
            'runtime': '52 ms',
            'memory': '14.1 MB',
            'total_correct': 31,
            'total_testcases': 31,
            'submission_id': '12345'
        }
        
        # Should not raise exception
        self.ui_manager.display_submission_result(result)
    
    def test_display_submission_result_failed(self):
        """Test displaying failed submission result."""
        result = {
            'status': 'completed',
            'status_code': 11,  # Wrong Answer
            'status_msg': 'Wrong Answer',
            'total_correct': 20,
            'total_testcases': 31,
            'submission_id': '12346'
        }
        
        # Should not raise exception
        self.ui_manager.display_submission_result(result)
    
    def test_display_submission_result_timeout(self):
        """Test displaying timeout submission result."""
        result = {
            'status': 'timeout',
            'error': 'Submission check timed out',
            'submission_id': '12347'
        }
        
        # Should not raise exception
        self.ui_manager.display_submission_result(result)
    
    def test_display_test_result_passed(self):
        """Test displaying passed test result."""
        result = {
            'status': 'completed',
            'run_success': True,
            'status_msg': 'Accepted',
            'total_correct': 3,
            'total_testcases': 3,
            'interpret_id': 'test123'
        }
        
        # Should not raise exception
        self.ui_manager.display_test_result(result)
    
    def test_display_test_result_failed(self):
        """Test displaying failed test result."""
        result = {
            'status': 'completed',
            'run_success': False,
            'status_msg': 'Wrong Answer',
            'total_correct': 2,
            'total_testcases': 3,
            'expected_output': '[1,2]',
            'code_output': '[1,3]',
            'last_testcase': '[2,7,11,15]\n9',
            'interpret_id': 'test124'
        }
        
        # Should not raise exception
        self.ui_manager.display_test_result(result)
    
    def test_display_submission_history_empty(self):
        """Test displaying empty submission history."""
        submissions = []
        username = 'testuser'
        
        # Should not raise exception
        self.ui_manager.display_submission_history(submissions, username)
    
    def test_display_submission_history_with_data(self):
        """Test displaying submission history with data."""
        submissions = [
            {
                'title': 'Two Sum',
                'status_display': 'Accepted',
                'lang': 'python3',
                'runtime': '52 ms',
                'memory': '14.1 MB',
                'timestamp': '1609459200'  # 2021-01-01 00:00:00
            },
            {
                'title': 'Add Two Numbers',
                'status_display': 'Wrong Answer',
                'lang': 'java',
                'runtime': 'N/A',
                'memory': 'N/A',
                'timestamp': '1609545600'  # 2021-01-02 00:00:00
            }
        ]
        username = 'testuser'
        
        # Should not raise exception
        self.ui_manager.display_submission_history(submissions, username)
    
    def test_display_stats_heatmap_empty(self):
        """Test displaying empty stats heatmap."""
        stats_data = {}
        
        # Should not raise exception
        self.ui_manager.display_stats_heatmap(stats_data)
    
    def test_display_stats_heatmap_with_data(self):
        """Test displaying stats heatmap with data."""
        stats_data = {
            'submission_calendar': {
                '1609459200': '5',  # 2021-01-01: 5 submissions
                '1609545600': '3',  # 2021-01-02: 3 submissions
                '1609632000': '1'   # 2021-01-03: 1 submission
            }
        }
        
        # Should not raise exception
        self.ui_manager.display_stats_heatmap(stats_data)
    
    def test_calculate_streak(self):
        """Test streak calculation."""
        from datetime import datetime, timedelta
        
        # Create test data for recent days
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        day_before = today - timedelta(days=2)
        
        year_data = {
            today.strftime('%Y-%m-%d'): 2,
            yesterday.strftime('%Y-%m-%d'): 1,
            day_before.strftime('%Y-%m-%d'): 3
        }
        
        streak = self.ui_manager._calculate_streak(year_data)
        self.assertEqual(streak, 3)  # 3-day streak
    
    def test_calculate_streak_broken(self):
        """Test streak calculation with broken streak."""
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        yesterday = today - timedelta(days=1)
        day_before = today - timedelta(days=2)
        
        year_data = {
            today.strftime('%Y-%m-%d'): 2,
            # No data for yesterday (breaks streak)
            day_before.strftime('%Y-%m-%d'): 3
        }
        
        streak = self.ui_manager._calculate_streak(year_data)
        self.assertEqual(streak, 1)  # Only today
    
    def test_display_progress_bars_empty(self):
        """Test displaying progress bars with empty data."""
        profile_data = {}
        
        # Should not raise exception
        self.ui_manager.display_progress_bars(profile_data)
    
    def test_display_progress_bars_with_data(self):
        """Test displaying progress bars with data."""
        profile_data = {
            'stats': {
                'total_solved': 150,
                'difficulty_breakdown': {
                    'Easy': {'solved': 80, 'total': 200},
                    'Medium': {'solved': 50, 'total': 150},
                    'Hard': {'solved': 20, 'total': 100}
                }
            },
            'recent_submissions': [
                {
                    'title': 'Two Sum',
                    'status': 'Accepted',
                    'timestamp': '1609459200'
                }
            ]
        }
        
        # Should not raise exception
        self.ui_manager.display_progress_bars(profile_data)
    
    def test_create_tui_menu(self):
        """Test TUI menu creation."""
        menu = self.ui_manager._create_tui_menu()
        
        self.assertIn('View Profile', menu)
        self.assertIn('Daily Challenge', menu)
        self.assertIn('Search Problems', menu)
        self.assertIn('Quit', menu)


if __name__ == '__main__':
    unittest.main()
