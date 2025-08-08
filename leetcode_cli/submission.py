"""Submission management for LeetCode CLI."""

import json
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from .auth import AuthManager
from .cache import CacheManager


class SubmissionManager:
    """Manages LeetCode submissions and test execution."""
    
    def __init__(self):
        self.auth = AuthManager()
        self.cache = CacheManager()
        self.session = self.auth.get_session()
    
    def submit_solution(self, problem_slug: str, file_path: str, language: str) -> Dict[str, Any]:
        """Submit a solution file to LeetCode."""
        if not self.auth.is_authenticated():
            raise Exception("Not authenticated. Please login first.")
        
        solution_content = self._read_solution_file(file_path)
        
        # Get problem details
        problem_data = self._get_problem_data(problem_slug)
        if not problem_data:
            raise Exception(f"Problem '{problem_slug}' not found.")
        
        # Submit the solution
        submission_data = {
            'lang': self._get_language_slug(language),
            'question_id': problem_data['id'],
            'typed_code': solution_content
        }
        
        submit_url = f"https://leetcode.com/problems/{problem_slug}/submit/"
        
        try:
            response = self.session.post(submit_url, json=submission_data)
            response.raise_for_status()
            
            result = response.json()
            submission_id = result.get('submission_id')
            
            if not submission_id:
                raise Exception("Failed to get submission ID")
            
            # Wait for and get submission result
            return self._wait_for_submission_result(submission_id)
            
        except requests.RequestException as e:
            raise Exception(f"Submission failed: {str(e)}")
    
    def run_test_cases(self, problem_slug: str, file_path: str, language: str) -> Dict[str, Any]:
        """Run test cases for a solution without submitting."""
        if not self.auth.is_authenticated():
            raise Exception("Not authenticated. Please login first.")
        
        solution_content = self._read_solution_file(file_path)
        
        # Get problem details
        problem_data = self._get_problem_data(problem_slug)
        if not problem_data:
            raise Exception(f"Problem '{problem_slug}' not found.")
        
        # Get test cases
        test_cases = self._get_test_cases(problem_slug)
        
        # Run tests
        test_data = {
            'lang': self._get_language_slug(language),
            'question_id': problem_data['id'],
            'typed_code': solution_content,
            'data_input': test_cases.get('data_input', ''),
            'judge_type': test_cases.get('judge_type', 'large')
        }
        
        test_url = f"https://leetcode.com/problems/{problem_slug}/interpret_solution/"
        
        try:
            response = self.session.post(test_url, json=test_data)
            response.raise_for_status()
            
            result = response.json()
            interpret_id = result.get('interpret_id')
            
            if not interpret_id:
                raise Exception("Failed to get test execution ID")
            
            # Wait for and get test result
            return self._wait_for_test_result(interpret_id)
            
        except requests.RequestException as e:
            raise Exception(f"Test execution failed: {str(e)}")
    
    def get_submission_history(self, username: str, problem_slug: str = None, 
                             status: str = None, language: str = None, 
                             limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's submission history with filters."""
        # Try cache first
        cache_key = f"submissions_{username}_{problem_slug or 'all'}_{status or 'all'}_{language or 'all'}"
        cached_submissions = self.cache.get_cached_stats(cache_key)
        if cached_submissions:
            return cached_submissions[:limit]
        
        submissions = []
        offset = 0
        
        while len(submissions) < limit:
            batch = self._fetch_submissions_batch(username, offset, min(20, limit - len(submissions)))
            if not batch:
                break
            
            # Apply filters
            filtered_batch = self._filter_submissions(batch, problem_slug, status, language)
            submissions.extend(filtered_batch)
            offset += 20
            
            # Avoid infinite loop
            if len(batch) < 20:
                break
        
        # Cache results
        self.cache.cache_stats(cache_key, submissions)
        
        return submissions[:limit]
    
    def get_submission_detail(self, submission_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific submission."""
        if not self.auth.is_authenticated():
            raise Exception("Not authenticated. Please login first.")
        
        detail_url = f"https://leetcode.com/submissions/detail/{submission_id}/"
        
        try:
            response = self.session.get(detail_url)
            response.raise_for_status()
            
            # Parse the response to extract submission details
            # This would require HTML parsing as LeetCode doesn't provide a direct API
            return self._parse_submission_detail(response.text)
            
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch submission details: {str(e)}")
    
    def _read_solution_file(self, file_path: str) -> str:
        """Read solution file content."""
        path = Path(file_path)
        if not path.exists():
            raise Exception(f"Solution file not found: {file_path}")
        
        try:
            return path.read_text(encoding='utf-8')
        except Exception as e:
            raise Exception(f"Failed to read solution file: {str(e)}")
    
    def _get_problem_data(self, problem_slug: str) -> Optional[Dict[str, Any]]:
        """Get problem data from cache or API."""
        cached = self.cache.get_cached_problem(problem_slug)
        if cached:
            return cached
        
        # Fetch from API
        query = '''
        query questionTitle($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                difficulty
                isPaidOnly
                topicTags {
                    name
                    slug
                }
            }
        }
        '''
        
        variables = {'titleSlug': problem_slug}
        
        try:
            response = self.session.post(
                'https://leetcode.com/graphql',
                json={'query': query, 'variables': variables}
            )
            response.raise_for_status()
            
            data = response.json()
            question = data.get('data', {}).get('question', {})
            
            if question:
                problem_data = {
                    'id': question.get('questionFrontendId'),
                    'title': question.get('title'),
                    'title_slug': question.get('titleSlug'),
                    'difficulty': question.get('difficulty'),
                    'is_paid_only': question.get('isPaidOnly', False),
                    'tags': [tag.get('name') for tag in question.get('topicTags', [])]
                }
                
                # Cache the result
                self.cache.cache_problem(problem_data)
                return problem_data
                
        except requests.RequestException:
            pass
        
        return None
    
    def _get_test_cases(self, problem_slug: str) -> Dict[str, Any]:
        """Get test cases for a problem."""
        test_url = f"https://leetcode.com/problems/{problem_slug}/"
        
        try:
            response = self.session.get(test_url)
            response.raise_for_status()
            
            # This would require parsing the HTML to extract test cases
            # For now, return empty test case data
            return {
                'data_input': '',
                'judge_type': 'large'
            }
            
        except requests.RequestException:
            return {'data_input': '', 'judge_type': 'large'}
    
    def _get_language_slug(self, language: str) -> str:
        """Convert language name to LeetCode language slug."""
        language_map = {
            'python': 'python3',
            'python3': 'python3',
            'java': 'java',
            'cpp': 'cpp',
            'c++': 'cpp',
            'c': 'c',
            'javascript': 'javascript',
            'js': 'javascript',
            'typescript': 'typescript',
            'ts': 'typescript',
            'go': 'golang',
            'golang': 'golang',
            'rust': 'rust',
            'ruby': 'ruby',
            'php': 'php',
            'swift': 'swift',
            'kotlin': 'kotlin',
            'scala': 'scala',
            'mysql': 'mysql',
            'postgresql': 'postgresql'
        }
        
        return language_map.get(language.lower(), language.lower())
    
    def _wait_for_submission_result(self, submission_id: str, timeout: int = 30) -> Dict[str, Any]:
        """Wait for submission result and return it."""
        check_url = f"https://leetcode.com/submissions/detail/{submission_id}/check/"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(check_url)
                response.raise_for_status()
                
                result = response.json()
                state = result.get('state', 'PENDING')
                
                if state == 'SUCCESS':
                    return {
                        'status': 'completed',
                        'status_code': result.get('status_code'),
                        'status_msg': result.get('status_msg'),
                        'runtime': result.get('runtime'),
                        'memory': result.get('memory'),
                        'total_correct': result.get('total_correct'),
                        'total_testcases': result.get('total_testcases'),
                        'submission_id': submission_id
                    }
                elif state in ['FAILURE', 'TIMEOUT']:
                    return {
                        'status': 'failed',
                        'error': result.get('status_msg', 'Unknown error'),
                        'submission_id': submission_id
                    }
                
                time.sleep(1)  # Wait before next check
                
            except requests.RequestException:
                time.sleep(1)
                continue
        
        return {
            'status': 'timeout',
            'error': 'Submission check timed out',
            'submission_id': submission_id
        }
    
    def _wait_for_test_result(self, interpret_id: str, timeout: int = 30) -> Dict[str, Any]:
        """Wait for test result and return it."""
        check_url = f"https://leetcode.com/submissions/detail/{interpret_id}/check/"
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = self.session.get(check_url)
                response.raise_for_status()
                
                result = response.json()
                state = result.get('state', 'PENDING')
                
                if state == 'SUCCESS':
                    return {
                        'status': 'completed',
                        'status_msg': result.get('status_msg'),
                        'run_success': result.get('run_success'),
                        'expected_output': result.get('expected_output', ''),
                        'code_output': result.get('code_output', ''),
                        'last_testcase': result.get('last_testcase', ''),
                        'total_correct': result.get('total_correct'),
                        'total_testcases': result.get('total_testcases'),
                        'interpret_id': interpret_id
                    }
                elif state in ['FAILURE', 'TIMEOUT']:
                    return {
                        'status': 'failed',
                        'error': result.get('status_msg', 'Unknown error'),
                        'interpret_id': interpret_id
                    }
                
                time.sleep(1)  # Wait before next check
                
            except requests.RequestException:
                time.sleep(1)
                continue
        
        return {
            'status': 'timeout',
            'error': 'Test execution timed out',
            'interpret_id': interpret_id
        }
    
    def _fetch_submissions_batch(self, username: str, offset: int, limit: int) -> List[Dict[str, Any]]:
        """Fetch a batch of submissions."""
        submissions_url = f"https://leetcode.com/api/submissions/?offset={offset}&limit={limit}&lastkey={username}"
        
        try:
            response = self.session.get(submissions_url)
            response.raise_for_status()
            
            data = response.json()
            return data.get('submissions_dump', [])
            
        except requests.RequestException:
            return []
    
    def _filter_submissions(self, submissions: List[Dict[str, Any]], 
                          problem_slug: str = None, status: str = None, 
                          language: str = None) -> List[Dict[str, Any]]:
        """Filter submissions based on criteria."""
        filtered = submissions
        
        if problem_slug:
            filtered = [s for s in filtered if s.get('title_slug') == problem_slug]
        
        if status:
            status_map = {
                'accepted': 'Accepted',
                'ac': 'Accepted',
                'wrong': 'Wrong Answer',
                'wa': 'Wrong Answer',
                'tle': 'Time Limit Exceeded',
                'mle': 'Memory Limit Exceeded',
                'ce': 'Compile Error',
                're': 'Runtime Error'
            }
            target_status = status_map.get(status.lower(), status)
            filtered = [s for s in filtered if s.get('status_display') == target_status]
        
        if language:
            lang_slug = self._get_language_slug(language)
            filtered = [s for s in filtered if s.get('lang') == lang_slug]
        
        return filtered
    
    def _parse_submission_detail(self, html_content: str) -> Dict[str, Any]:
        """Parse submission detail from HTML (placeholder implementation)."""
        # This would require proper HTML parsing with BeautifulSoup
        # For now, return basic structure
        return {
            'code': '',
            'status': 'Unknown',
            'runtime': 'N/A',
            'memory': 'N/A',
            'language': 'Unknown'
        }