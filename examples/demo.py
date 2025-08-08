#!/usr/bin/env python3
"""
LeetCode CLI Demo Script

This script demonstrates all the available features of the LeetCode CLI.
Run this to see examples of each command in action.

Usage: python3 demo.py [username]
"""

import sys
import subprocess
import time
from pathlib import Path


def run_command(cmd: list, description: str):
    """Run a CLI command and display the result."""
    print(f"\n{'='*60}")
    print(f"🔥 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print(result.stdout)
        else:
            print(f"❌ Error: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⏱️ Command timed out")
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    print("\n" + "⏸️" * 20 + " Press Enter to continue " + "⏸️" * 20)
    input()


def main():
    """Main demo function."""
    username = sys.argv[1] if len(sys.argv) > 1 else "leetcode"
    
    print("🚀 LeetCode CLI Feature Demonstration")
    print(f"Using username: {username}")
    print("\nThis demo will showcase all available commands.")
    print("Press Enter to start...")
    input()
    
    # Command demonstrations
    commands = [
        (
            ["python3", "-m", "leetcode_cli", "--help"],
            "CLI Help - Overview of all commands"
        ),
        (
            ["python3", "-m", "leetcode_cli", "profile", username],
            f"User Profile - View {username}'s profile and statistics"
        ),
        (
            ["python3", "-m", "leetcode_cli", "daily"],
            "Daily Challenge - Today's featured problem"
        ),
        (
            ["python3", "-m", "leetcode_cli", "search", "two sum", "--limit", "5"],
            "Problem Search - Find problems matching 'two sum'"
        ),
        (
            ["python3", "-m", "leetcode_cli", "search", "array", "--difficulty", "Easy", "--limit", "3"],
            "Filtered Search - Easy array problems"
        ),
        (
            ["python3", "-m", "leetcode_cli", "problem", "two-sum"],
            "Problem Details - View 'Two Sum' problem details"
        ),
        (
            ["python3", "-m", "leetcode_cli", "stats", username, "--progress"],
            f"Statistics with Progress - {username}'s solving progress"
        ),
        (
            ["python3", "-m", "leetcode_cli", "stats", username, "--heatmap"],
            f"Activity Heatmap - {username}'s submission calendar"
        ),
        (
            ["python3", "-m", "leetcode_cli", "cache", "--stats"],
            "Cache Statistics - Local cache information"
        ),
        (
            ["python3", "-m", "leetcode_cli", "submissions", username, "--limit", "5"],
            f"Recent Submissions - {username}'s latest submissions"
        )
    ]
    
    # Run each command demonstration
    for cmd, description in commands:
        run_command(cmd, description)
    
    # Show solution submission example (without actually submitting)
    print(f"\n{'='*60}")
    print("💾 Solution Submission Example")
    print(f"{'='*60}")
    print("To submit a solution, you would use:")
    print("  leetcode submit two-sum examples/two_sum.py --lang python3")
    print("\nTo test without submitting:")
    print("  leetcode test two-sum examples/two_sum.py --lang python3")
    print("\nNote: These commands require authentication (leetcode login)")
    
    # Show example solution file
    solution_file = Path("examples/two_sum.py")
    if solution_file.exists():
        print("\n📝 Example solution file (examples/two_sum.py):")
        print("-" * 40)
        print(solution_file.read_text())
    
    print(f"\n{'='*60}")
    print("🎯 Demo Complete!")
    print(f"{'='*60}")
    print("All features demonstrated! Key takeaways:")
    print("• Rich terminal output with colors and formatting")
    print("• Comprehensive user profiles and statistics")
    print("• Problem search and detailed information")
    print("• Submission and testing capabilities")
    print("• Local caching for improved performance")
    print("• JSON output support for automation")
    print("\nTo get started:")
    print("1. Install: pip install -e .")
    print("2. Login: leetcode login")
    print("3. Explore: leetcode --help")
    print("\nHappy coding! 🚀")


if __name__ == "__main__":
    main()
