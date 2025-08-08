"""Profile management for LeetCode CLI."""

import requests
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from .auth import AuthManager


class ProfileManager:
    """Manages user profile operations."""
    
    def __init__(self):
        self.auth_manager = AuthManager()
        self.session = self.auth_manager.get_session()
    
    def get_user_profile(self, username: str) -> Dict[str, Any]:
        """Fetch user profile information."""
        # GraphQL query for user profile
        query = """
        query getUserProfile($username: String!) {
            matchedUser(username: $username) {
                username
                profile {
                    userAvatar
                    realName
                    aboutMe
                    school
                    websites
                    countryName
                    company
                    jobTitle
                    skillTags
                    postViewCount
                    postViewCountDiff
                    reputation
                    reputationDiff
                    solutionCount
                    solutionCountDiff
                    categoryDiscussCount
                    categoryDiscussCountDiff
                }
                submitStats: submitStatsGlobal {
                    acSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                    totalSubmissionNum {
                        difficulty
                        count
                        submissions
                    }
                }
                badges {
                    id
                    displayName
                    icon
                    creationDate
                }
                upcomingBadges {
                    name
                    icon
                    progress
                }
                activeBadge {
                    id
                    displayName
                    icon
                }
            }
            userContestRanking(username: $username) {
                attendedContestsCount
                rating
                globalRanking
                totalParticipants
                topPercentage
                badge {
                    name
                }
            }
            userContestRankingHistory(username: $username) {
                attended
                trendDirection
                problemsSolved
                totalProblems
                finishTimeInSeconds
                rating
                ranking
                contest {
                    title
                    startTime
                }
            }
        }
        """
        
        variables = {"username": username}
        
        response = self._make_graphql_request(query, variables)
        
        if not response or 'data' not in response:
            raise Exception("Failed to fetch user profile")
        
        matched_user = response['data'].get('matchedUser')
        if not matched_user:
            raise Exception(f"User '{username}' not found")
        
        contest_ranking = response['data'].get('userContestRanking')
        
        # Process the data
        profile_data = {
            'username': matched_user['username'],
            'profile': matched_user.get('profile', {}),
            'stats': self._process_submit_stats(matched_user.get('submitStats', {})),
            'badges': matched_user.get('badges', []),
            'upcoming_badges': matched_user.get('upcomingBadges', []),
            'active_badge': matched_user.get('activeBadge'),
            'contest_ranking': contest_ranking,
            'avatar_url': matched_user.get('profile', {}).get('userAvatar'),
            'submission_calendar': self._get_submission_calendar(username),
            'recent_submissions': self._get_recent_submissions(username)
        }
        
        return profile_data
    
    def _process_submit_stats(self, submit_stats: Dict) -> Dict[str, Any]:
        """Process submission statistics."""
        if not submit_stats:
            return {}
        
        ac_stats = submit_stats.get('acSubmissionNum', [])
        total_stats = submit_stats.get('totalSubmissionNum', [])
        
        stats = {
            'total_solved': 0,
            'total_submissions': 0,
            'acceptance_rate': 0.0,
            'difficulty_breakdown': {
                'Easy': {'solved': 0, 'total': 0, 'acceptance_rate': 0.0},
                'Medium': {'solved': 0, 'total': 0, 'acceptance_rate': 0.0},
                'Hard': {'solved': 0, 'total': 0, 'acceptance_rate': 0.0}
            }
        }
        
        # Process accepted submissions
        for stat in ac_stats:
            difficulty = stat.get('difficulty', 'All')
            count = stat.get('count', 0)
            
            if difficulty == 'All':
                stats['total_solved'] = count
            elif difficulty in stats['difficulty_breakdown']:
                stats['difficulty_breakdown'][difficulty]['solved'] = count
        
        # Process total submissions
        for stat in total_stats:
            difficulty = stat.get('difficulty', 'All')
            submissions = stat.get('submissions', 0)
            
            if difficulty == 'All':
                stats['total_submissions'] = submissions
            elif difficulty in stats['difficulty_breakdown']:
                stats['difficulty_breakdown'][difficulty]['total'] = submissions
        
        # Calculate acceptance rates
        if stats['total_submissions'] > 0:
            stats['acceptance_rate'] = (stats['total_solved'] / stats['total_submissions']) * 100
        
        for difficulty_stats in stats['difficulty_breakdown'].values():
            if difficulty_stats['total'] > 0:
                difficulty_stats['acceptance_rate'] = (
                    difficulty_stats['solved'] / difficulty_stats['total']
                ) * 100
        
        return stats
    
    def _get_avatar_url(self, username: str) -> Optional[str]:
        """Get user avatar URL."""
        try:
            # Try to get avatar from LeetCode's user page
            response = self.session.get(f'https://leetcode.com/{username}/')
            if response.status_code == 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for avatar image
                avatar_img = soup.find('img', {'class': 'avatar'}) or soup.find('img', class_='h-24')
                if avatar_img and avatar_img.get('src'):
                    return avatar_img['src']
        except Exception:
            pass
        
        return None
    
    def get_avatar_ascii(self, image_url: str, width: int = 16) -> str:
        """Convert avatar image to ASCII art."""
        try:
            # Download the image
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate', 
                'Connection': 'keep-alive',
            }
            response = requests.get(image_url, headers=headers)
            response.raise_for_status()
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            try:
                # Calculate height to maintain aspect ratio
                height = max(6, width // 2)
                
                # Use the best working configuration from testing
                result = subprocess.run([
                    'chafa', '--size', f'{width}x{height}', '--format', 'symbols', 
                    '--symbols', 'block', tmp_path
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0 and result.stdout.strip():
                    return result.stdout.strip()
                
                # Fallback to text avatar - extract username from URL or use generic
                username = image_url.split('/')[-2] if '/users/' in image_url else 'User'
                return self._create_text_avatar(username)
                
            finally:
                Path(tmp_path).unlink(missing_ok=True)
                
        except Exception as e:
            # Create fallback text avatar - extract username from URL or use generic  
            username = image_url.split('/')[-2] if '/users/' in image_url else 'User'
            return self._create_text_avatar(username)

    def _create_text_avatar(self, username: str) -> str:
        """Create a simple text-based avatar as fallback."""
        initials = ''.join([c.upper() for c in username[:2] if c.isalnum()])
        if not initials:
            initials = username[0].upper() if username else '?'
        
        # Create a simple bordered avatar
        border = '═' * 8
        top_left = '╔'
        top_right = '╗'  
        side = '║'
        bottom_left = '╚'
        bottom_right = '╝'
        
        avatar = f"""{top_left}{border}{top_right}
{side}        {side}
{side}   {initials:<2}   {side}
{side}        {side}
{bottom_left}{border}{bottom_right}"""
        return avatar.strip()
    
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
    
    def _get_submission_calendar(self, username: str) -> Dict[str, int]:
        """Get user's submission calendar data for heatmap."""
        query = """
        query userProfileCalendar($username: String!) {
            matchedUser(username: $username) {
                submissionCalendar
            }
        }
        """
        
        variables = {"username": username}
        response = self._make_graphql_request(query, variables)
        
        if response and 'data' in response:
            matched_user = response['data'].get('matchedUser', {})
            calendar_data = matched_user.get('submissionCalendar', '{}')
            
            try:
                import json
                return json.loads(calendar_data) if calendar_data else {}
            except (json.JSONDecodeError, TypeError):
                return {}
        
        return {}
    
    def _get_recent_submissions(self, username: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get user's recent submission history."""
        query = """
        query recentSubmissions($username: String!, $limit: Int) {
            recentSubmissionList(username: $username, limit: $limit) {
                title
                titleSlug
                timestamp
                statusDisplay
                lang
                runtime
                url
            }
        }
        """
        
        variables = {"username": username, "limit": limit}
        response = self._make_graphql_request(query, variables)
        
        if response and 'data' in response:
            submissions = response['data'].get('recentSubmissionList', [])
            return submissions
        
        return []
