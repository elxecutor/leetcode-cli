"""Cache management for LeetCode CLI."""

import json
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional


class CacheManager:
    """Manages local SQLite cache for LeetCode data."""
    
    def __init__(self, cache_ttl: int = 3600):  # 1 hour default TTL
        self.cache_dir = Path.home() / '.config' / 'leetcode-cli'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.db_path = self.cache_dir / 'cache.db'
        self.cache_ttl = cache_ttl
        self._init_database()
    
    def _init_database(self):
        """Initialize the cache database."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Problems cache table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS problems_cache (
                    id INTEGER PRIMARY KEY,
                    title TEXT,
                    title_slug TEXT UNIQUE,
                    difficulty TEXT,
                    acceptance_rate REAL,
                    is_paid_only BOOLEAN,
                    tags TEXT,  -- JSON array
                    content TEXT,
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # User profiles cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS profiles_cache (
                    username TEXT PRIMARY KEY,
                    profile_data TEXT,  -- JSON data
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Daily challenges cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_cache (
                    date TEXT PRIMARY KEY,
                    challenge_data TEXT,  -- JSON data
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Submissions cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS submissions_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    problem_slug TEXT,
                    submission_data TEXT,  -- JSON data
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Statistics cache
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stats_cache (
                    key TEXT PRIMARY KEY,
                    value TEXT,  -- JSON data
                    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper cleanup."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _is_cache_valid(self, cached_at: str) -> bool:
        """Check if cached data is still valid."""
        try:
            cached_time = datetime.fromisoformat(cached_at.replace('Z', '+00:00'))
            return datetime.utcnow() - cached_time < timedelta(seconds=self.cache_ttl)
        except (ValueError, AttributeError):
            return False
    
    def cache_problem(self, problem_data: Dict[str, Any]):
        """Cache problem data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO problems_cache 
                (id, title, title_slug, difficulty, acceptance_rate, is_paid_only, tags, content)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                problem_data.get('id'),
                problem_data.get('title'),
                problem_data.get('title_slug'),
                problem_data.get('difficulty'),
                problem_data.get('acceptance_rate'),
                problem_data.get('is_paid_only'),
                json.dumps(problem_data.get('tags', [])),
                problem_data.get('content', '')
            ))
            
            conn.commit()
    
    def get_cached_problem(self, problem_slug: str) -> Optional[Dict[str, Any]]:
        """Get cached problem data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM problems_cache 
                WHERE title_slug = ? 
                ORDER BY cached_at DESC 
                LIMIT 1
            ''', (problem_slug,))
            
            row = cursor.fetchone()
            if row and self._is_cache_valid(row['cached_at']):
                return {
                    'id': row['id'],
                    'title': row['title'],
                    'title_slug': row['title_slug'],
                    'difficulty': row['difficulty'],
                    'acceptance_rate': row['acceptance_rate'],
                    'is_paid_only': bool(row['is_paid_only']),
                    'tags': json.loads(row['tags']) if row['tags'] else [],
                    'content': row['content']
                }
            return None
    
    def cache_profile(self, username: str, profile_data: Dict[str, Any]):
        """Cache user profile data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO profiles_cache 
                (username, profile_data)
                VALUES (?, ?)
            ''', (username, json.dumps(profile_data)))
            
            conn.commit()
    
    def get_cached_profile(self, username: str) -> Optional[Dict[str, Any]]:
        """Get cached profile data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT profile_data, cached_at FROM profiles_cache 
                WHERE username = ?
            ''', (username,))
            
            row = cursor.fetchone()
            if row and self._is_cache_valid(row['cached_at']):
                return json.loads(row['profile_data'])
            return None
    
    def cache_daily_challenge(self, date: str, challenge_data: Dict[str, Any]):
        """Cache daily challenge data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO daily_cache 
                (date, challenge_data)
                VALUES (?, ?)
            ''', (date, json.dumps(challenge_data)))
            
            conn.commit()
    
    def get_cached_daily_challenge(self, date: str) -> Optional[Dict[str, Any]]:
        """Get cached daily challenge data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT challenge_data, cached_at FROM daily_cache 
                WHERE date = ?
            ''', (date,))
            
            row = cursor.fetchone()
            if row and self._is_cache_valid(row['cached_at']):
                return json.loads(row['challenge_data'])
            return None
    
    def cache_submissions(self, username: str, problem_slug: str, submissions: List[Dict[str, Any]]):
        """Cache user submissions for a problem."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Clear old submissions for this problem
            cursor.execute('''
                DELETE FROM submissions_cache 
                WHERE username = ? AND problem_slug = ?
            ''', (username, problem_slug))
            
            # Insert new submissions
            for submission in submissions:
                cursor.execute('''
                    INSERT INTO submissions_cache 
                    (username, problem_slug, submission_data)
                    VALUES (?, ?, ?)
                ''', (username, problem_slug, json.dumps(submission)))
            
            conn.commit()
    
    def get_cached_submissions(self, username: str, problem_slug: str = None) -> List[Dict[str, Any]]:
        """Get cached submissions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if problem_slug:
                cursor.execute('''
                    SELECT submission_data, cached_at FROM submissions_cache 
                    WHERE username = ? AND problem_slug = ?
                    ORDER BY cached_at DESC
                ''', (username, problem_slug))
            else:
                cursor.execute('''
                    SELECT submission_data, cached_at FROM submissions_cache 
                    WHERE username = ?
                    ORDER BY cached_at DESC
                ''', (username,))
            
            submissions = []
            for row in cursor.fetchall():
                if self._is_cache_valid(row['cached_at']):
                    submissions.append(json.loads(row['submission_data']))
            
            return submissions
    
    def cache_stats(self, key: str, stats_data: Any):
        """Cache statistics data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO stats_cache 
                (key, value)
                VALUES (?, ?)
            ''', (key, json.dumps(stats_data)))
            
            conn.commit()
    
    def get_cached_stats(self, key: str) -> Optional[Any]:
        """Get cached statistics."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT value, cached_at FROM stats_cache 
                WHERE key = ?
            ''', (key,))
            
            row = cursor.fetchone()
            if row and self._is_cache_valid(row['cached_at']):
                return json.loads(row['value'])
            return None
    
    def clear_cache(self, table: str = None):
        """Clear cache data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if table:
                cursor.execute(f'DELETE FROM {table}_cache')
            else:
                # Clear all caches
                tables = ['problems', 'profiles', 'daily', 'submissions', 'stats']
                for table_name in tables:
                    cursor.execute(f'DELETE FROM {table_name}_cache')
            
            conn.commit()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics."""
        stats = {}
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            tables = ['problems', 'profiles', 'daily', 'submissions', 'stats']
            for table in tables:
                cursor.execute(f'SELECT COUNT(*) FROM {table}_cache')
                count = cursor.fetchone()[0]
                stats[f'{table}_count'] = count
        
        return stats
    
    def cleanup_expired(self):
        """Remove expired cache entries."""
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.cache_ttl)
        cutoff_str = cutoff_time.isoformat()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            tables = ['problems', 'profiles', 'daily', 'submissions', 'stats']
            removed_count = 0
            
            for table in tables:
                cursor.execute(f'''
                    DELETE FROM {table}_cache 
                    WHERE cached_at < ?
                ''', (cutoff_str,))
                removed_count += cursor.rowcount
            
            conn.commit()
            
        return removed_count
