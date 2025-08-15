# 🚀 LeetCode CLI Companion

A comprehensive, feature-rich terminal-based CLI tool for LeetCode. View profiles, submit solutions, track progress, and more - all from your terminal with beautiful ASCII art and rich formatting!

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Tests](https://img.shields.io/badge/tests-25%20passed-brightgreen.svg)](#)

## ✨ Features

- 👤 **User Profiles**: Fetch and display user profiles with ASCII avatar art
- 📅 **Daily Challenges**: Get today's LeetCode daily challenge
- 🔍 **Problem Search**: Search problems by keywords, tags, or difficulty
- 📋 **Problem Details**: View complete problem descriptions with metadata
- 💾 **Submit Solutions**: Submit solution files and get verdict, runtime, and memory usage
- 🧪 **Test Runner**: Run test cases locally before submitting
- 📈 **Submission History**: View and filter your submission history
- 🏆 **Statistics**: Display solving stats, streaks, and heatmaps
- 📊 **Progress Tracking**: Interactive progress bars and activity visualization
- 🖥️ **TUI Mode**: Interactive terminal user interface
- 💾 **Smart Caching**: Local SQLite cache for faster performance
- 🎨 **Rich UI**: Beautiful terminal output with colors and formatting
- 🔐 **Authentication**: Secure login with session cookies
- 📊 **JSON Output**: Perfect for scripting and automation

## 🛠 Installation
## ▶️ How to Run

After installing, you can run the CLI as a Python module:

```bash
python3 -m leetcode_cli [command] [options]
```

For example:
```bash
python3 -m leetcode_cli profile elxecutor
python3 -m leetcode_cli daily
python3 -m leetcode_cli search "two sum"
python3 -m leetcode_cli submit two-sum examples/two_sum.py --lang python3
```

You do not need to install any separate `leetcode` command. All usage examples in this README should be run by replacing `leetcode` with `python3 -m leetcode_cli`.

You can also run any example or test script directly:
```bash
python3 examples/demo.py
```

### From Source

```bash
git clone https://github.com/elxecutor/leetcode-cli.git
cd leetcode-cli
pip install -e .
```

### Development Installation

```bash
git clone https://github.com/elxecutor/leetcode-cli.git
cd leetcode-cli
make dev  # or pip install -e ".[dev]"
```

### Dependencies

The CLI requires Python 3.8+ and optionally [chafa](https://github.com/hpjansson/chafa) for ASCII avatar rendering:

```bash
# On Ubuntu/Debian
sudo apt install chafa

# On macOS
brew install chafa

# On Arch Linux
sudo pacman -S chafa
```

### 🚀 Quick Start

### Basic Usage

```bash
# View a user's profile
python3 -m leetcode_cli profile elxecutor

# Get today's daily challenge
python3 -m leetcode_cli daily

# Search for problems
python3 -m leetcode_cli search "two sum"

# View specific problem details
python3 -m leetcode_cli problem two-sum

# Submit a solution (requires authentication)
python3 -m leetcode_cli submit two-sum examples/two_sum.py --lang python3

# Run tests without submitting
python3 -m leetcode_cli test two-sum examples/two_sum.py --lang python3

# View submission history
python3 -m leetcode_cli submissions elxecutor --status accepted --lang python3

# Display statistics with heatmap
python3 -m leetcode_cli stats elxecutor --heatmap

# Start interactive TUI mode
python3 -m leetcode_cli tui

# Get help
python3 -m leetcode_cli --help
```

### Demo Script

Try out all features with our comprehensive demo:

```bash
# Run interactive demo
python3 examples/demo.py [username]
```

### Authentication (Required for Submissions)

To submit solutions and access personalized features:

```bash
python3 -m leetcode_cli login
```

## 📖 Commands

### `profile USERNAME`

Display comprehensive user profile information including:
- Basic profile details (name, company, location)
- Problem-solving statistics by difficulty
- Contest rankings and ratings
- Recent badges and achievements
- ASCII art avatar (if `chafa` is installed)

```bash
# Examples
leetcode profile leetcode
leetcode profile elxecutor --json
```

### `daily`

Show today's daily LeetCode challenge with:
- Problem metadata (difficulty, acceptance rate)
- Tags and topics
- Your completion status (if logged in)
- Direct link to the problem

```bash
leetcode daily
leetcode daily --json
```

### `search QUERY`

Search problems by keywords or tags:

```bash
# Search by problem name
leetcode search "binary search"

# Filter by difficulty
leetcode search "tree" --difficulty Hard

# Limit results
leetcode search "array" --limit 20

# JSON output for scripting
leetcode search "dynamic programming" --json
```

### `problem ID_OR_SLUG`

View detailed problem information:

```bash
# By problem ID
leetcode problem 1

# By problem slug
leetcode problem two-sum

# JSON format
leetcode problem 146 --json
```

### `submit PROBLEM_SLUG FILE_PATH --lang LANGUAGE`

Submit solution files to LeetCode:

```bash
# Submit Python solution
leetcode submit two-sum examples/two_sum.py --lang python3

# Submit Java solution  
leetcode submit add-two-numbers Solution.java --lang java

# Submit with JSON output
leetcode submit valid-parentheses examples/two_sum.py --lang python3 --json
```

### `test PROBLEM_SLUG FILE_PATH --lang LANGUAGE`

Run test cases without submitting:

```bash
# Test Python solution
leetcode test two-sum examples/two_sum.py --lang python3

# Test with specific language
leetcode test binary-search solution.cpp --lang cpp
```

### `submissions USERNAME`

View and filter submission history:

```bash
# View recent submissions
leetcode submissions elxecutor

# Filter by problem
leetcode submissions elxecutor --problem two-sum

# Filter by status
leetcode submissions elxecutor --status accepted

# Filter by language
leetcode submissions elxecutor --lang python3 --limit 50
```

### `stats USERNAME`

Display comprehensive statistics:

```bash
# Basic statistics
leetcode stats elxecutor

# Show activity heatmap
leetcode stats elxecutor --heatmap

# Show interactive progress bars
leetcode stats elxecutor --progress
```

### `tui`

Start interactive Terminal User Interface:

```bash
# Launch TUI mode
leetcode tui
```

### `cache`

Manage local cache:

```bash
# View cache statistics
leetcode cache --stats

# Clear all cached data
leetcode cache --clear

# Remove expired entries
leetcode cache --cleanup
```

### `login` / `logout`

Manage authentication:

```bash
# Interactive login
leetcode login

# Logout and clear credentials
leetcode logout
```

## 📁 Examples

The `examples/` directory contains:

- `two_sum.py` - Sample Python solution for the Two Sum problem
- `demo.py` - Interactive demonstration of all CLI features
- `README.md` - Guide for using example files

```bash
# Try the demo
python3 examples/demo.py

# Use example solution
leetcode submit two-sum examples/two_sum.py --lang python3
```

## ⚙️ Configuration

The CLI stores configuration in `~/.config/leetcode-cli/`:

- `auth.json`: Authentication credentials (securely stored)
- `cache.db`: Local SQLite cache for problems, profiles, and submissions

### Performance Features

- **Smart Caching**: Automatic SQLite-based caching reduces API calls
- **Offline Mode**: View cached problems and profiles without internet
- **Background Processing**: Non-blocking submission status checking
- **Efficient Filtering**: Local filtering of large datasets
- **Minimal Dependencies**: Lightweight with optional enhancements

## 🔧 Development

### Setup Development Environment

```bash
git clone https://github.com/elxecutor/leetcode-cli.git
cd leetcode-cli
make dev
```

### Run Tests

```bash
make test
```

### Code Formatting

```bash
make format  # Format with black
make lint    # Check with flake8 and mypy
```

### Project Structure

```
leetcode_cli/
├── __init__.py      # Package initialization
├── __main__.py      # CLI entry point
├── auth.py          # Authentication management
├── cache.py         # Local SQLite caching system
├── main.py          # CLI application and commands
├── problem.py       # Problem search and details
├── profile.py       # User profile operations  
├── submission.py    # Solution submission and testing
└── ui.py            # Rich terminal UI components

examples/
├── README.md        # Example usage guide
├── demo.py          # Feature demonstration script
└── two_sum.py       # Sample solution file

tests/
├── conftest.py      # Test configuration
├── test_*.py        # Test modules
└── ...
```

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is not officially associated with LeetCode. It uses LeetCode's public APIs and follows their terms of service. Please use responsibly.

---

Made with ❤️ for the LeetCode community
