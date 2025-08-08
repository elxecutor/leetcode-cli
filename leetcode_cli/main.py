#!/usr/bin/env python3
"""Main CLI application for LeetCode CLI."""

from typing import Optional

import typer
from rich.console import Console

from .auth import AuthManager
from .problem import ProblemManager
from .profile import ProfileManager
from .submission import SubmissionManager
from .ui import UIManager

app = typer.Typer(
    name="leetcode",
    help="A terminal-based CLI tool to interact with LeetCode",
    rich_markup_mode="rich"
)

console = Console()
ui_manager = UIManager(console)


@app.command("profile")
def show_profile(
    username: str = typer.Argument(..., help="LeetCode username"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """Fetch and display user profile information."""
    try:
        profile_manager = ProfileManager()
        profile_data = profile_manager.get_user_profile(username)
        
        if json_output:
            ui_manager.print_json(profile_data)
        else:
            ui_manager.display_profile(profile_data)
            
    except Exception as e:
        ui_manager.print_error(f"Failed to fetch profile: {str(e)}")
        raise typer.Exit(1)


@app.command("daily")
def daily_challenge(
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """Retrieve and show today's daily LeetCode challenge."""
    try:
        problem_manager = ProblemManager()
        daily_problem = problem_manager.get_daily_challenge()
        
        if json_output:
            ui_manager.print_json(daily_problem)
        else:
            ui_manager.display_daily_challenge(daily_problem)
            
    except Exception as e:
        ui_manager.print_error(f"Failed to fetch daily challenge: {str(e)}")
        raise typer.Exit(1)


@app.command("search")
def search_problems(
    query: str = typer.Argument(..., help="Search query (keyword or tag)"),
    difficulty: Optional[str] = typer.Option(None, help="Filter by difficulty (Easy, Medium, Hard)"),
    limit: int = typer.Option(10, help="Maximum number of results"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """Search problems by keyword or tag."""
    try:
        problem_manager = ProblemManager()
        problems = problem_manager.search_problems(
            query=query,
            difficulty=difficulty,
            limit=limit
        )
        
        if json_output:
            ui_manager.print_json(problems)
        else:
            ui_manager.display_search_results(problems, query)
            
    except Exception as e:
        ui_manager.print_error(f"Failed to search problems: {str(e)}")
        raise typer.Exit(1)


@app.command("problem")
def show_problem(
    problem_id: str = typer.Argument(..., help="Problem ID or slug"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """View problem metadata and description."""
    try:
        problem_manager = ProblemManager()
        problem_data = problem_manager.get_problem_details(problem_id)
        
        if json_output:
            ui_manager.print_json(problem_data)
        else:
            ui_manager.display_problem_details(problem_data)
            
    except Exception as e:
        ui_manager.print_error(f"Failed to fetch problem details: {str(e)}")
        raise typer.Exit(1)


@app.command("login")
def login():
    """Login to LeetCode using session cookie or credentials."""
    try:
        auth_manager = AuthManager()
        success = auth_manager.interactive_login()
        
        if success:
            ui_manager.print_success("Successfully logged in to LeetCode!")
        else:
            ui_manager.print_error("Login failed. Please check your credentials.")
            raise typer.Exit(1)
            
    except Exception as e:
        ui_manager.print_error(f"Login error: {str(e)}")
        raise typer.Exit(1)


@app.command("logout")
def logout():
    """Logout and clear stored credentials."""
    try:
        auth_manager = AuthManager()
        auth_manager.logout()
        ui_manager.print_success("Successfully logged out!")
        
    except Exception as e:
        ui_manager.print_error(f"Logout error: {str(e)}")
        raise typer.Exit(1)


@app.command("submit")
def submit_solution(
    problem_slug: str = typer.Argument(..., help="Problem slug (e.g., two-sum)"),
    file_path: str = typer.Argument(..., help="Path to solution file"),
    language: str = typer.Option(..., "--lang", "-l", help="Programming language"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """Submit a solution file to LeetCode."""
    try:
        submission_manager = SubmissionManager()
        result = submission_manager.submit_solution(problem_slug, file_path, language)
        
        if json_output:
            ui_manager.print_json(result)
        else:
            ui_manager.display_submission_result(result)
            
    except Exception as e:
        ui_manager.print_error(f"Submission failed: {str(e)}")
        raise typer.Exit(1)


@app.command("test")
def test_solution(
    problem_slug: str = typer.Argument(..., help="Problem slug (e.g., two-sum)"),
    file_path: str = typer.Argument(..., help="Path to solution file"),
    language: str = typer.Option(..., "--lang", "-l", help="Programming language"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """Run test cases for a solution without submitting."""
    try:
        submission_manager = SubmissionManager()
        result = submission_manager.run_test_cases(problem_slug, file_path, language)
        
        if json_output:
            ui_manager.print_json(result)
        else:
            ui_manager.display_test_result(result)
            
    except Exception as e:
        ui_manager.print_error(f"Test execution failed: {str(e)}")
        raise typer.Exit(1)


@app.command("submissions")
def list_submissions(
    username: str = typer.Argument(..., help="LeetCode username"),
    problem: Optional[str] = typer.Option(None, "--problem", "-p", help="Filter by problem slug"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status (accepted, wrong, etc.)"),
    language: Optional[str] = typer.Option(None, "--lang", "-l", help="Filter by programming language"),
    limit: int = typer.Option(20, "--limit", help="Maximum number of submissions to show"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """List and filter user submission history."""
    try:
        submission_manager = SubmissionManager()
        submissions = submission_manager.get_submission_history(
            username=username,
            problem_slug=problem,
            status=status,
            language=language,
            limit=limit
        )
        
        if json_output:
            ui_manager.print_json(submissions)
        else:
            ui_manager.display_submission_history(submissions, username)
            
    except Exception as e:
        ui_manager.print_error(f"Failed to fetch submissions: {str(e)}")
        raise typer.Exit(1)


@app.command("stats")
def show_stats(
    username: str = typer.Argument(..., help="LeetCode username"),
    heatmap: bool = typer.Option(False, "--heatmap", help="Show activity heatmap"),
    progress: bool = typer.Option(False, "--progress", help="Show progress bars"),
    json_output: bool = typer.Option(False, "--json", help="Output in JSON format")
):
    """Display user statistics, streaks, and heatmaps."""
    try:
        profile_manager = ProfileManager()
        profile_data = profile_manager.get_user_profile(username)
        
        if json_output:
            ui_manager.print_json(profile_data)
            return
        
        if heatmap:
            ui_manager.display_stats_heatmap(profile_data)
        elif progress:
            ui_manager.display_progress_bars(profile_data)
        else:
            # Show both stats and basic info
            ui_manager.display_profile(profile_data)
            ui_manager.display_progress_bars(profile_data)
            
    except Exception as e:
        ui_manager.print_error(f"Failed to fetch statistics: {str(e)}")
        raise typer.Exit(1)


@app.command("tui")
def interactive_mode():
    """Start interactive TUI (Terminal User Interface) mode."""
    try:
        ui_manager.start_tui_mode()
        
    except KeyboardInterrupt:
        ui_manager.print_info("TUI mode interrupted by user")
    except Exception as e:
        ui_manager.print_error(f"TUI mode error: {str(e)}")
        raise typer.Exit(1)


@app.command("cache")
def cache_management(
    clear: bool = typer.Option(False, "--clear", help="Clear all cached data"),
    stats: bool = typer.Option(False, "--stats", help="Show cache statistics"),
    cleanup: bool = typer.Option(False, "--cleanup", help="Remove expired cache entries")
):
    """Manage local cache data."""
    try:
        from .cache import CacheManager
        cache_manager = CacheManager()
        
        if clear:
            cache_manager.clear_cache()
            ui_manager.print_success("Cache cleared successfully!")
        elif cleanup:
            removed = cache_manager.cleanup_expired()
            ui_manager.print_success(f"Removed {removed} expired cache entries")
        elif stats:
            cache_stats = cache_manager.get_cache_stats()
            ui_manager.print_json(cache_stats)
        else:
            ui_manager.print_info("Use --clear, --stats, or --cleanup flags")
            
    except Exception as e:
        ui_manager.print_error(f"Cache operation failed: {str(e)}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
