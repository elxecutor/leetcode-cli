"""Problem management module for LeetCode CLI."""

import re
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests

from .auth import AuthManager


class ProblemManager:
    """Manages LeetCode problem operations."""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.session = self.auth_manager.get_session()
    
    def get_daily_challenge(self) -> Dict[str, Any]:
        """Get today's daily challenge."""
        query = """
        query questionOfToday {
            activeDailyCodingChallengeQuestion {
                date
                userStatus
                link
                question {
                    acRate
                    difficulty
                    freqBar
                    frontendQuestionId: questionFrontendId
                    isFavor
                    paidOnly: isPaidOnly
                    status
                    title
                    titleSlug
                    hasVideoSolution
                    hasSolution
                    topicTags {
                        name
                        id
                        slug
                    }
                }
            }
        }
        """
        
        response = self._make_graphql_request(query)
        
        if not response or 'data' not in response:
            raise Exception("Failed to fetch daily challenge")
        
        daily_challenge = response['data'].get('activeDailyCodingChallengeQuestion')
        if not daily_challenge:
            raise Exception("No daily challenge found")
        
        question = daily_challenge['question']
        
        return {
            'date': daily_challenge['date'],
            'link': daily_challenge['link'],
            'user_status': daily_challenge.get('userStatus'),
            'problem': {
                'id': question['frontendQuestionId'],
                'title': question['title'],
                'title_slug': question['titleSlug'],
                'difficulty': question['difficulty'],
                'acceptance_rate': round(question['acRate'], 2),
                'is_paid_only': question['paidOnly'],
                'status': question.get('status'),
                'tags': [tag['name'] for tag in question.get('topicTags', [])],
                'has_solution': question.get('hasSolution', False),
                'has_video_solution': question.get('hasVideoSolution', False)
            }
        }
    
    def search_problems(self, query: str, difficulty: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Search problems by keyword or tag."""
        # Get all problems first
        all_problems = self.get_all_problems()
        
        if not all_problems:
            raise Exception("Failed to fetch problems list")
        
        # Filter problems
        filtered_problems = []
        query_lower = query.lower()
        
        for problem in all_problems:
            # Search in title and tags
            title_match = query_lower in problem['title'].lower()
            tag_match = any(query_lower in tag.lower() for tag in problem.get('tags', []))
            
            if title_match or tag_match:
                # Apply difficulty filter if specified
                if difficulty and problem['difficulty'].lower() != difficulty.lower():
                    continue
                
                filtered_problems.append(problem)
                
                if len(filtered_problems) >= limit:
                    break
        
        return filtered_problems
    
    def get_all_problems(self) -> List[Dict[str, Any]]:
        """Get list of all problems."""
        try:
            response = self.session.get('https://leetcode.com/api/problems/all/')
            response.raise_for_status()
            data = response.json()
            
            problems = []
            for problem in data.get('stat_status_pairs', []):
                stat = problem.get('stat', {})
                difficulty = problem.get('difficulty', {})
                
                problems.append({
                    'id': stat.get('frontend_question_id'),
                    'title': stat.get('question__title', ''),
                    'title_slug': stat.get('question__title_slug', ''),
                    'difficulty': difficulty.get('level_name', 'Unknown'),
                    'acceptance_rate': round(
                        self._safe_calculate_acceptance_rate(
                            stat.get('total_acs', 0), 
                            stat.get('total_submitted', 1)
                        ), 2
                    ),
                    'is_paid_only': problem.get('paid_only', False),
                    'status': problem.get('status'),
                    'tags': []  # Tags need separate API call
                })
            
            return problems
        except requests.RequestException:
            return []
    
    def get_problem_details(self, problem_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific problem."""
        # Determine if problem_id is numeric ID or slug
        if problem_id.isdigit():
            # Need to find slug from numeric ID
            all_problems = self.get_all_problems()
            problem_slug = None
            for problem in all_problems:
                try:
                    # Safely compare problem IDs
                    if problem.get('id') is not None:
                        problem_id_str = str(problem['id'])
                        if problem_id_str == problem_id:
                            problem_slug = problem['title_slug']
                            break
                except (ValueError, TypeError):
                    continue
            
            if not problem_slug:
                raise Exception(f"Problem with ID {problem_id} not found")
        else:
            problem_slug = problem_id
        
        query = """
        query questionData($titleSlug: String!) {
            question(titleSlug: $titleSlug) {
                questionId
                questionFrontendId
                title
                titleSlug
                content
                translatedTitle
                translatedContent
                isPaidOnly
                difficulty
                likes
                dislikes
                isLiked
                similarQuestions
                contributors {
                    username
                    profileUrl
                    avatarUrl
                    __typename
                }
                langToValidPlayground
                topicTags {
                    name
                    slug
                    translatedName
                    __typename
                }
                companyTagStats
                codeSnippets {
                    lang
                    langSlug
                    code
                    __typename
                }
                stats
                hints
                solution {
                    id
                    canSeeDetail
                    __typename
                }
                status
                sampleTestCase
                metaData
                judgerAvailable
                judgeType
                mysqlSchemas
                enableRunCode
                envInfo
                __typename
            }
        }
        """
        
        variables = {"titleSlug": problem_slug}
        response = self._make_graphql_request(query, variables)
        
        if not response or 'data' not in response:
            raise Exception("Failed to fetch problem details")
        
        question = response['data'].get('question')
        if not question:
            raise Exception(f"Problem '{problem_slug}' not found")
        
        # Parse stats
        stats = {}
        if question.get('stats'):
            import json
            try:
                stats_data = json.loads(question['stats'])
                # Safely convert to integers
                try:
                    total_accepted = int(stats_data.get('totalAccepted', 0))
                except (ValueError, TypeError):
                    total_accepted = 0
                
                try:
                    total_submission = int(stats_data.get('totalSubmission', 1))
                except (ValueError, TypeError):
                    total_submission = 1
                
                stats = {
                    'total_accepted': total_accepted,
                    'total_submission': total_submission,
                    'acceptance_rate': round(
                        (total_accepted / max(total_submission, 1)) * 100, 2
                    )
                }
            except (json.JSONDecodeError, KeyError):
                pass
        
        return {
            'id': question['questionFrontendId'],
            'title': question['title'],
            'title_slug': question['titleSlug'],
            'content': question['content'],
            'difficulty': question['difficulty'],
            'is_paid_only': question['isPaidOnly'],
            'likes': question.get('likes', 0),
            'dislikes': question.get('dislikes', 0),
            'tags': [tag['name'] for tag in question.get('topicTags', [])],
            'hints': question.get('hints', []),
            'sample_test_case': question.get('sampleTestCase', ''),
            'code_snippets': question.get('codeSnippets', []),
            'stats': stats,
            'status': question.get('status'),
            'has_solution': bool(question.get('solution'))
        }
    
    def get_problem_content_markdown(self, content: str) -> str:
        """Convert problem HTML content to markdown-friendly format."""
        if not content:
            return ""
        
        # Basic HTML to markdown conversion
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(content, 'html.parser')
        
        # Convert common HTML tags
        for tag in soup.find_all(['strong', 'b']):
            tag.string = f"**{tag.get_text()}**"
            tag.unwrap()
        
        for tag in soup.find_all(['em', 'i']):
            tag.string = f"*{tag.get_text()}*"
            tag.unwrap()
        
        for tag in soup.find_all('code'):
            tag.string = f"`{tag.get_text()}`"
            tag.unwrap()
        
        for tag in soup.find_all('pre'):
            content = tag.get_text()
            tag.string = f"\n```\n{content}\n```\n"
            tag.unwrap()
        
        # Convert lists
        for ul in soup.find_all('ul'):
            items = []
            for li in ul.find_all('li'):
                items.append(f"- {li.get_text().strip()}")
            ul.string = "\n" + "\n".join(items) + "\n"
            ul.unwrap()
        
        for ol in soup.find_all('ol'):
            items = []
            for i, li in enumerate(ol.find_all('li'), 1):
                items.append(f"{i}. {li.get_text().strip()}")
            ol.string = "\n" + "\n".join(items) + "\n"
            ol.unwrap()
        
        # Clean up and return
        text = soup.get_text()
        
        # Clean up extra whitespace
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = text.strip()
        
        return text
    
    def _safe_calculate_acceptance_rate(self, total_acs, total_submitted):
        """Safely calculate acceptance rate handling various data types."""
        try:
            acs = int(total_acs) if total_acs is not None else 0
            submitted = int(total_submitted) if total_submitted is not None else 1
            if submitted == 0:
                return 0.0
            return (acs / submitted) * 100
        except (ValueError, TypeError):
            return 0.0
    
    def _make_graphql_request(self, query: str, variables: Dict = None) -> Optional[Dict]:
        """Make a GraphQL request to LeetCode API."""
        url = 'https://leetcode.com/graphql'
        
        payload = {
            'query': query,
            'variables': variables or {}
        }
        
        headers = {
            'Content-Type': 'application/json',
            'Referer': 'https://leetcode.com'
        }
        
        try:
            response = self.session.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException:
            return None
