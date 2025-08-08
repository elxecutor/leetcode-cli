"""UI module for LeetCode CLI with rich terminal output."""

import json
from datetime import datetime
from typing import Any, Dict, List

from rich.columns import Columns
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TextColumn, TimeElapsedColumn
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


class UIManager:
    """Manages UI rendering and display."""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
    
    def print_success(self, message: str):
        """Print success message."""
        self.console.print(f"✅ {message}", style="bold green")
    
    def print_error(self, message: str):
        """Print error message."""
        self.console.print(f"❌ {message}", style="bold red")
    
    def print_warning(self, message: str):
        """Print warning message."""
        self.console.print(f"⚠️  {message}", style="bold yellow")
    
    def print_info(self, message: str):
        """Print info message."""
        self.console.print(f"ℹ️  {message}", style="bold blue")
    
    def print_json(self, data: Any):
        """Print data as formatted JSON."""
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        self.console.print(json_str)
    
    def display_profile(self, profile_data: Dict[str, Any]):
        """Display user profile information."""
        username = profile_data.get('username', 'Unknown')
        profile = profile_data.get('profile', {})
        stats = profile_data.get('stats', {})
        
        # Create main profile panel
        profile_info = []
        
        if profile.get('realName'):
            profile_info.append(f"[bold]Real Name:[/bold] {profile['realName']}")
        
        if profile.get('company'):
            profile_info.append(f"[bold]Company:[/bold] {profile['company']}")
        
        if profile.get('jobTitle'):
            profile_info.append(f"[bold]Job Title:[/bold] {profile['jobTitle']}")
        
        if profile.get('school'):
            profile_info.append(f"[bold]School:[/bold] {profile['school']}")
        
        if profile.get('countryName'):
            profile_info.append(f"[bold]Location:[/bold] {profile['countryName']}")
        
        profile_text = "\n".join(profile_info) if profile_info else "No profile information available"
        
        # Display avatar if available
        avatar_url = profile_data.get('avatar_url')
        username = profile_data.get('username', 'Unknown')
        
        if avatar_url:
            from .profile import ProfileManager
            profile_manager = ProfileManager()
            ascii_art = profile_manager.get_avatar_ascii(avatar_url, width=20)  # Balanced size
            
            if not ascii_art:
                # Fallback to text avatar if chafa fails or produces poor results
                ascii_art = profile_manager._create_text_avatar(username)
            
            if ascii_art:
                # Handle ANSI codes properly with Rich
                from rich.text import Text
                
                # Create Rich Text object that can handle ANSI codes
                if '\x1b[' in ascii_art:  # Contains ANSI escape codes
                    avatar_text = Text.from_ansi(ascii_art)
                else:
                    avatar_text = ascii_art
                
                # Create a centered avatar display with equal padding
                avatar_panel = Panel(
                    avatar_text,
                    title=f"👤 {username}",
                    border_style="cyan",
                    width=36,  # Wider to accommodate padding
                    padding=(1, 2),  # Equal padding: (top/bottom, left/right)
                    expand=False,  # Don't expand to full width
                    title_align="center"  # Center the title
                )
                self.console.print(avatar_panel)
        
        # Display profile panel
        profile_panel = Panel(
            profile_text,
            title=f"👤 Profile: {username}",
            border_style="blue"
        )
        self.console.print(profile_panel)
        
        # Display statistics
        if stats:
            self._display_stats(stats)
        
        # Display badges
        badges = profile_data.get('badges', [])
        if badges:
            self._display_badges(badges[:5])  # Show first 5 badges
        
        # Display contest ranking
        contest_ranking = profile_data.get('contest_ranking')
        if contest_ranking:
            self._display_contest_ranking(contest_ranking)
    
    def _display_stats(self, stats: Dict[str, Any]):
        """Display user statistics."""
        table = Table(title="📊 Problem Solving Statistics")
        table.add_column("Difficulty", style="cyan", no_wrap=True)
        table.add_column("Solved", style="green")
        table.add_column("Total Submissions", style="yellow")
        table.add_column("Acceptance Rate", style="magenta")
        
        difficulty_breakdown = stats.get('difficulty_breakdown', {})
        
        for difficulty, data in difficulty_breakdown.items():
            solved = data.get('solved', 0)
            total = data.get('total', 0)
            acceptance_rate = data.get('acceptance_rate', 0.0)
            
            # Color code by difficulty
            difficulty_style = {
                'Easy': 'green',
                'Medium': 'yellow',
                'Hard': 'red'
            }.get(difficulty, 'white')
            
            table.add_row(
                Text(difficulty, style=difficulty_style),
                str(solved),
                str(total),
                f"{acceptance_rate:.1f}%"
            )
        
        # Add total row
        total_solved = stats.get('total_solved', 0)
        total_submissions = stats.get('total_submissions', 0)
        overall_acceptance_rate = stats.get('acceptance_rate', 0.0)
        
        table.add_row(
            Text("Total", style="bold"),
            Text(str(total_solved), style="bold green"),
            Text(str(total_submissions), style="bold yellow"),
            Text(f"{overall_acceptance_rate:.1f}%", style="bold magenta")
        )
        
        self.console.print(table)
    
    def _display_badges(self, badges: List[Dict[str, Any]]):
        """Display user badges."""
        if not badges:
            return
        
        badge_text = []
        for badge in badges:
            name = badge.get('displayName', 'Unknown Badge')
            date = badge.get('creationDate')
            if date:
                try:
                    date_obj = datetime.fromtimestamp(int(date))
                    date_str = date_obj.strftime('%Y-%m-%d')
                    badge_text.append(f"🏆 **{name}** ({date_str})")
                except (ValueError, TypeError):
                    badge_text.append(f"🏆 **{name}**")
            else:
                badge_text.append(f"🏆 **{name}**")
        
        badges_panel = Panel(
            "\n".join(badge_text),
            title="🏆 Recent Badges",
            border_style="yellow"
        )
        self.console.print(badges_panel)
    
    def _display_contest_ranking(self, contest_ranking: Dict[str, Any]):
        """Display contest ranking information."""
        if not contest_ranking:
            return
        
        ranking_info = []
        
        attended = contest_ranking.get('attendedContestsCount', 0)
        ranking_info.append(f"**Contests Attended:** {attended}")
        
        rating = contest_ranking.get('rating')
        if rating:
            ranking_info.append(f"**Rating:** {rating:.0f}")
        
        global_ranking = contest_ranking.get('globalRanking')
        if global_ranking:
            ranking_info.append(f"**Global Ranking:** {global_ranking:,}")
        
        top_percentage = contest_ranking.get('topPercentage')
        if top_percentage:
            ranking_info.append(f"**Top Percentage:** {top_percentage:.1f}%")
        
        badge = contest_ranking.get('badge')
        if badge and badge.get('name'):
            ranking_info.append(f"**Badge:** {badge['name']}")
        
        if ranking_info:
            contest_panel = Panel(
                "\n".join(ranking_info),
                title="🏁 Contest Performance",
                border_style="purple"
            )
            self.console.print(contest_panel)
    
    def display_daily_challenge(self, daily_data: Dict[str, Any]):
        """Display daily challenge information."""
        date = daily_data.get('date', '')
        problem = daily_data.get('problem', {})
        user_status = daily_data.get('user_status')
        
        title = f"📅 Daily Challenge - {date}"
        
        # Problem info
        problem_info = []
        problem_info.append(f"**#{problem.get('id')}** {problem.get('title', 'Unknown')}")
        
        difficulty = problem.get('difficulty', 'Unknown')
        difficulty_style = {
            'Easy': 'green',
            'Medium': 'yellow', 
            'Hard': 'red'
        }.get(difficulty, 'white')
        
        difficulty_text = Text(f"Difficulty: {difficulty}", style=difficulty_style)
        problem_info.append(str(difficulty_text))
        
        acceptance_rate = problem.get('acceptance_rate', 0)
        problem_info.append(f"**Acceptance Rate:** {acceptance_rate}%")
        
        tags = problem.get('tags', [])
        if tags:
            problem_info.append(f"**Tags:** {', '.join(tags[:5])}")  # Show first 5 tags
        
        if user_status:
            status_style = "green" if user_status == "ac" else "yellow"
            problem_info.append(f"**Status:** {Text(user_status.upper(), style=status_style)}")
        
        link = daily_data.get('link', '')
        if link:
            problem_info.append(f"**Link:** https://leetcode.com{link}")
        
        daily_panel = Panel(
            "\n".join(str(info) for info in problem_info),
            title=title,
            border_style="green"
        )
        self.console.print(daily_panel)
    
    def display_search_results(self, problems: List[Dict[str, Any]], query: str):
        """Display search results."""
        if not problems:
            self.print_warning(f"No problems found matching '{query}'")
            return
        
        table = Table(title=f"🔍 Search Results for '{query}'")
        table.add_column("ID", style="cyan", width=6)
        table.add_column("Title", style="white", min_width=30)
        table.add_column("Difficulty", style="white", width=10)
        table.add_column("Acceptance", style="green", width=12)
        table.add_column("Status", style="blue", width=8)
        
        for problem in problems:
            problem_id = str(problem.get('id', ''))
            title = problem.get('title', 'Unknown')
            difficulty = problem.get('difficulty', 'Unknown')
            acceptance_rate = problem.get('acceptance_rate', 0)
            status = problem.get('status') or 'Not Attempted'
            
            # Color code difficulty
            difficulty_style = {
                'Easy': 'green',
                'Medium': 'yellow',
                'Hard': 'red'
            }.get(difficulty, 'white')
            
            # Color code status
            status_color = {
                'ac': 'green',
                'notac': 'red',
                None: 'dim'
            }.get(status, 'dim')
            
            table.add_row(
                problem_id,
                title,
                Text(difficulty, style=difficulty_style),
                f"{acceptance_rate}%",
                Text(status if status != 'Not Attempted' else '—', style=status_color)
            )
        
        self.console.print(table)
        
        if len(problems) >= 10:
            self.print_info("Use --limit parameter to see more results")
    
    def display_problem_details(self, problem_data: Dict[str, Any]):
        """Display detailed problem information."""
        title = problem_data.get('title', 'Unknown')
        problem_id = problem_data.get('id', '')
        difficulty = problem_data.get('difficulty', 'Unknown')
        
        # Header
        header = f"#{problem_id} {title}"
        
        # Difficulty badge
        difficulty_style = {
            'Easy': 'green',
            'Medium': 'yellow',
            'Hard': 'red'
        }.get(difficulty, 'white')
        
        # Problem metadata
        metadata = []
        metadata.append(f"**Difficulty:** {Text(difficulty, style=difficulty_style)}")
        
        stats = problem_data.get('stats', {})
        if stats:
            acceptance_rate = stats.get('acceptance_rate', 0)
            metadata.append(f"**Acceptance Rate:** {acceptance_rate}%")
            
            total_accepted = stats.get('total_accepted', 0)
            total_submission = stats.get('total_submission', 0)
            metadata.append(f"**Submissions:** {total_accepted:,} / {total_submission:,}")
        
        likes = problem_data.get('likes', 0)
        dislikes = problem_data.get('dislikes', 0)
        if likes or dislikes:
            metadata.append(f"**Likes/Dislikes:** 👍 {likes} / 👎 {dislikes}")
        
        tags = problem_data.get('tags', [])
        if tags:
            metadata.append(f"**Tags:** {', '.join(tags)}")
        
        status = problem_data.get('status')
        if status:
            status_style = "green" if status == "ac" else "yellow"
            metadata.append(f"**Status:** {Text(status.upper(), style=status_style)}")
        
        # Display metadata panel
        metadata_panel = Panel(
            "\n".join(str(item) for item in metadata),
            title=header,
            border_style="blue"
        )
        self.console.print(metadata_panel)
        
        # Display problem content
        content = problem_data.get('content', '')
        if content:
            from .problem import ProblemManager
            problem_manager = ProblemManager()
            markdown_content = problem_manager.get_problem_content_markdown(content)
            
            if markdown_content:
                try:
                    md = Markdown(markdown_content)
                    content_panel = Panel(
                        md,
                        title="📋 Problem Description",
                        border_style="green"
                    )
                    self.console.print(content_panel)
                except Exception:
                    # Fallback to plain text if markdown parsing fails
                    content_panel = Panel(
                        markdown_content,
                        title="📋 Problem Description",
                        border_style="green"
                    )
                    self.console.print(content_panel)
        
        # Display hints if available
        hints = problem_data.get('hints', [])
        if hints:
            hint_text = []
            for i, hint in enumerate(hints, 1):
                hint_text.append(f"**Hint {i}:** {hint}")
            
            hints_panel = Panel(
                "\n\n".join(hint_text),
                title="💡 Hints",
                border_style="yellow"
            )
            self.console.print(hints_panel)
        
        # Display sample test case
        sample_test = problem_data.get('sample_test_case', '')
        if sample_test:
            test_panel = Panel(
                f"```\n{sample_test}\n```",
                title="🧪 Sample Test Case",
                border_style="cyan"
            )
            self.console.print(test_panel)
    
    def display_submission_result(self, result: Dict[str, Any]):
        """Display submission result."""
        status = result.get('status', 'unknown')
        
        if status == 'completed':
            status_code = result.get('status_code', 0)
            status_msg = result.get('status_msg', 'Unknown')
            
            # Determine status color
            status_color = "green" if status_code == 10 else "red"  # 10 = Accepted
            
            info_lines = []
            info_lines.append(f"**Status:** {Text(status_msg, style=status_color)}")
            
            runtime = result.get('runtime')
            if runtime:
                info_lines.append(f"**Runtime:** {runtime}")
            
            memory = result.get('memory')
            if memory:
                info_lines.append(f"**Memory:** {memory}")
            
            total_correct = result.get('total_correct')
            total_testcases = result.get('total_testcases')
            if total_correct is not None and total_testcases is not None:
                info_lines.append(f"**Test Cases:** {total_correct}/{total_testcases}")
            
            submission_id = result.get('submission_id')
            if submission_id:
                info_lines.append(f"**Submission ID:** {submission_id}")
            
            title = "✅ Submission Accepted" if status_code == 10 else "❌ Submission Failed"
            border_color = "green" if status_code == 10 else "red"
            
        elif status == 'timeout':
            info_lines = [f"**Error:** {result.get('error', 'Unknown timeout error')}"]
            title = "⏱️ Submission Timeout"
            border_color = "yellow"
            
        else:  # failed
            info_lines = [f"**Error:** {result.get('error', 'Unknown error')}"]
            title = "❌ Submission Failed"
            border_color = "red"
        
        result_panel = Panel(
            "\n".join(str(line) for line in info_lines),
            title=title,
            border_style=border_color
        )
        self.console.print(result_panel)
    
    def display_test_result(self, result: Dict[str, Any]):
        """Display test execution result."""
        status = result.get('status', 'unknown')
        
        if status == 'completed':
            run_success = result.get('run_success', False)
            status_msg = result.get('status_msg', 'Unknown')
            
            # Determine status color
            status_color = "green" if run_success else "red"
            
            info_lines = []
            info_lines.append(f"**Status:** {Text(status_msg, style=status_color)}")
            
            total_correct = result.get('total_correct')
            total_testcases = result.get('total_testcases')
            if total_correct is not None and total_testcases is not None:
                info_lines.append(f"**Test Cases Passed:** {total_correct}/{total_testcases}")
            
            # Show test case details if failed
            if not run_success:
                expected_output = result.get('expected_output', '')
                code_output = result.get('code_output', '')
                last_testcase = result.get('last_testcase', '')
                
                if last_testcase:
                    info_lines.append(f"**Last Test Case:** {last_testcase}")
                if expected_output:
                    info_lines.append(f"**Expected Output:** {expected_output}")
                if code_output:
                    info_lines.append(f"**Your Output:** {code_output}")
            
            interpret_id = result.get('interpret_id')
            if interpret_id:
                info_lines.append(f"**Test ID:** {interpret_id}")
            
            title = "✅ Tests Passed" if run_success else "❌ Tests Failed"
            border_color = "green" if run_success else "red"
            
        elif status == 'timeout':
            info_lines = [f"**Error:** {result.get('error', 'Unknown timeout error')}"]
            title = "⏱️ Test Timeout"
            border_color = "yellow"
            
        else:  # failed
            info_lines = [f"**Error:** {result.get('error', 'Unknown error')}"]
            title = "❌ Test Execution Failed"
            border_color = "red"
        
        result_panel = Panel(
            "\n".join(str(line) for line in info_lines),
            title=title,
            border_style=border_color
        )
        self.console.print(result_panel)
    
    def display_submission_history(self, submissions: List[Dict[str, Any]], username: str):
        """Display submission history."""
        if not submissions:
            self.print_warning(f"No submissions found for user '{username}'")
            return
        
        table = Table(title=f"📋 Submission History for {username}")
        table.add_column("Problem", style="cyan", min_width=20)
        table.add_column("Status", style="white", width=15)
        table.add_column("Language", style="blue", width=12)
        table.add_column("Runtime", style="green", width=10)
        table.add_column("Memory", style="yellow", width=10)
        table.add_column("Timestamp", style="dim", width=12)
        
        for submission in submissions:
            title = submission.get('title', 'Unknown')
            status = submission.get('status_display', 'Unknown')
            language = submission.get('lang', 'Unknown')
            runtime = submission.get('runtime', 'N/A')
            memory = submission.get('memory', 'N/A')
            timestamp = submission.get('timestamp', '')
            
            # Color code status
            status_color = {
                'Accepted': 'green',
                'Wrong Answer': 'red',
                'Time Limit Exceeded': 'yellow',
                'Memory Limit Exceeded': 'yellow',
                'Runtime Error': 'red',
                'Compile Error': 'red'
            }.get(status, 'white')
            
            # Format timestamp
            if timestamp:
                try:
                    from datetime import datetime
                    ts = datetime.fromtimestamp(int(timestamp))
                    timestamp_str = ts.strftime('%m-%d %H:%M')
                except (ValueError, TypeError):
                    timestamp_str = 'Unknown'
            else:
                timestamp_str = 'Unknown'
            
            table.add_row(
                title,
                Text(status, style=status_color),
                language,
                runtime,
                memory,
                timestamp_str
            )
        
        self.console.print(table)
    
    def display_stats_heatmap(self, stats_data: Dict[str, Any]):
        """Display problem-solving streak or heatmap in ASCII."""
        submission_calendar = stats_data.get('submission_calendar', {})
        
        if not submission_calendar:
            self.print_warning("No submission calendar data available")
            return
        
        # Create a simple text-based heatmap
        from datetime import datetime, timedelta
        
        # Get current year data
        current_year = datetime.now().year
        year_data = {}
        
        for date_str, count in submission_calendar.items():
            try:
                timestamp = int(date_str)
                date = datetime.fromtimestamp(timestamp)
                if date.year == current_year:
                    year_data[date.strftime('%Y-%m-%d')] = int(count)
            except (ValueError, TypeError):
                continue
        
        if not year_data:
            self.print_warning("No submission data for current year")
            return
        
        # Create heatmap representation
        heatmap_lines = []
        heatmap_lines.append("📊 Submission Activity Heatmap (Current Year)")
        heatmap_lines.append("=" * 50)
        
        # Group by months
        months_data = {}
        for date_str, count in year_data.items():
            month = date_str[:7]  # YYYY-MM
            if month not in months_data:
                months_data[month] = []
            months_data[month].append(count)
        
        # Display monthly stats
        for month in sorted(months_data.keys()):
            counts = months_data[month]
            total = sum(counts)
            avg = total / len(counts) if counts else 0
            max_count = max(counts) if counts else 0
            
            # Create simple bar representation
            bar_length = min(20, max(1, int(total / 5))) if total > 0 else 0
            bar = "█" * bar_length
            
            month_name = datetime.strptime(month, '%Y-%m').strftime('%b %Y')
            heatmap_lines.append(f"{month_name:10} {bar:20} {total:3d} submissions (avg: {avg:.1f}, max: {max_count})")
        
        # Calculate streak
        streak = self._calculate_streak(year_data)
        if streak > 0:
            heatmap_lines.append("")
            heatmap_lines.append(f"🔥 Current streak: {streak} days")
        
        heatmap_panel = Panel(
            "\n".join(heatmap_lines),
            title="📈 Activity Stats",
            border_style="green"
        )
        self.console.print(heatmap_panel)
    
    def _calculate_streak(self, year_data: Dict[str, int]) -> int:
        """Calculate current solving streak."""
        if not year_data:
            return 0
        
        from datetime import datetime, timedelta
        
        today = datetime.now().date()
        streak = 0
        
        # Check backwards from today
        current_date = today
        while True:
            date_str = current_date.strftime('%Y-%m-%d')
            if year_data.get(date_str, 0) > 0:
                streak += 1
                current_date -= timedelta(days=1)
            else:
                break
        
        return streak
    
    def display_progress_bars(self, profile_data: Dict[str, Any]):
        """Display interactive progress bars for user stats."""
        stats = profile_data.get('stats', {})
        difficulty_breakdown = stats.get('difficulty_breakdown', {})
        
        if not difficulty_breakdown:
            self.print_warning("No statistics available for progress display")
            return
        
        self.console.print("\n📊 Problem Solving Progress", style="bold blue")
        
        # Create progress bars for each difficulty
        for difficulty, data in difficulty_breakdown.items():
            solved = data.get('solved', 0)
            total = data.get('total', 1)  # Avoid division by zero
            percentage = (solved / total) * 100 if total > 0 else 0
            
            # Color code by difficulty
            color = {
                'Easy': 'green',
                'Medium': 'yellow',
                'Hard': 'red'
            }.get(difficulty, 'white')
            
            # Create progress bar
            with Progress(
                TextColumn("[bold blue]{task.fields[difficulty]}"),
                BarColumn(bar_width=None),
                "[progress.percentage]{task.percentage:>3.1f}%",
                "•",
                TextColumn("{task.fields[solved]}/{task.fields[total_problems]}"),
                console=self.console,
                expand=True
            ) as progress:
                
                task = progress.add_task(
                    f"{difficulty}",
                    total=100,
                    completed=percentage,
                    difficulty=difficulty,
                    solved=solved,
                    total_problems=total
                )
                
                # Show the progress bar briefly
                import time
                time.sleep(0.1)
        
        # Overall progress
        total_solved = stats.get('total_solved', 0)
        total_problems = sum(d.get('total', 0) for d in difficulty_breakdown.values())
        overall_percentage = (total_solved / total_problems * 100) if total_problems > 0 else 0
        
        self.console.print(f"\n🎯 Overall Progress: {total_solved}/{total_problems} ({overall_percentage:.1f}%)", style="bold")
        
        # Show recent activity if available
        recent_submissions = profile_data.get('recent_submissions', [])
        if recent_submissions:
            self.console.print("\n🔄 Recent Activity:", style="bold green")
            for submission in recent_submissions[:5]:  # Show last 5
                title = submission.get('title', 'Unknown')
                status = submission.get('status', 'Unknown')
                timestamp = submission.get('timestamp', '')
                
                if timestamp:
                    try:
                        from datetime import datetime
                        dt = datetime.fromtimestamp(int(timestamp))
                        time_str = dt.strftime('%m-%d %H:%M')
                    except (ValueError, TypeError):
                        time_str = 'Unknown'
                else:
                    time_str = 'Unknown'
                
                status_icon = "✅" if status == "Accepted" else "❌"
                self.console.print(f"  {status_icon} {title} - {time_str}")
    
    def start_tui_mode(self):
        """Start interactive TUI mode."""
        try:
            from rich.live import Live
            from rich.layout import Layout
            from rich.align import Align
            import threading
            import time
            
            # Create layout
            layout = Layout()
            layout.split_column(
                Layout(name="header", size=3),
                Layout(name="body"),
                Layout(name="footer", size=3)
            )
            
            # Split body into sidebar and main
            layout["body"].split_row(
                Layout(name="sidebar", minimum_size=30),
                Layout(name="main")
            )
            
            # Header
            header = Panel(
                Align.center("🚀 LeetCode CLI - Interactive Mode", vertical="middle"),
                style="bold blue"
            )
            layout["header"].update(header)
            
            # Footer
            footer = Panel(
                Align.center("Press 'q' to quit • Use arrow keys to navigate", vertical="middle"),
                style="dim"
            )
            layout["footer"].update(footer)
            
            # Sidebar menu
            menu = Panel(
                self._create_tui_menu(),
                title="📋 Menu",
                border_style="green"
            )
            layout["sidebar"].update(menu)
            
            # Main content
            main_content = Panel(
                "Welcome to LeetCode CLI Interactive Mode!\n\nSelect an option from the menu to get started.",
                title="📖 Content",
                border_style="blue"
            )
            layout["main"].update(main_content)
            
            # Start live display
            with Live(layout, refresh_per_second=4):
                self.console.print("TUI Mode started! (This is a basic implementation)")
                self.console.print("In a full implementation, this would be interactive...")
                time.sleep(5)  # Simulate TUI interaction
                
        except ImportError:
            self.print_error("TUI mode requires additional dependencies. Install with: pip install textual")
        except Exception as e:
            self.print_error(f"Failed to start TUI mode: {str(e)}")
    
    def _create_tui_menu(self) -> str:
        """Create TUI menu options."""
        menu_items = [
            "1. View Profile",
            "2. Daily Challenge", 
            "3. Search Problems",
            "4. View Problem",
            "5. Submit Solution",
            "6. Test Solution",
            "7. View Submissions",
            "8. Statistics",
            "",
            "q. Quit"
        ]
        return "\n".join(menu_items)
