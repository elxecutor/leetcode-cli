.PHONY: install dev test lint format clean run help

# Default target
help:
	@echo "Available targets:"
	@echo "  install     Install the package in development mode"
	@echo "  dev         Install development dependencies"
	@echo "  test        Run tests"
	@echo "  lint        Run linters (flake8, mypy)"
	@echo "  format      Format code with black"
	@echo "  clean       Clean up build artifacts"
	@echo "  run         Run the CLI (example usage)"
	@echo "  help        Show this help message"

install:
	pip3 install -e .

dev:
	pip3 install -e ".[dev]"
	pip3 install pytest pytest-cov black flake8 mypy

test:
	python3 -m pytest tests/ -v --cov=leetcode_cli --cov-report=html --cov-report=term

lint:
	python3 -m flake8 leetcode_cli/
	python3 -m mypy leetcode_cli/

format:
	python3 -m black leetcode_cli/ tests/

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	@echo "Example usage:"
	@echo "  leetcode profile octocat"
	@echo "  leetcode daily"
	@echo "  leetcode search 'two sum'"
	@echo "  leetcode problem 1"
	@echo "  leetcode login"
