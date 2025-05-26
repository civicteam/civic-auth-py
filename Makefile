.PHONY: help install dev lint format test build clean publish publish-test

help:
	@echo "Available commands:"
	@echo "  install      Install the package in editable mode"
	@echo "  dev          Install with all dev dependencies"
	@echo "  lint         Run linting checks (ruff, mypy)"
	@echo "  format       Format code with black"
	@echo "  test         Run tests"
	@echo "  build        Build distribution packages"
	@echo "  clean        Clean build artifacts"
	@echo "  publish-test Publish to TestPyPI"
	@echo "  publish      Publish to PyPI"

install:
	pip install -e .

dev:
	pip install -e ".[all,dev]"

lint:
	ruff check civic_auth tests
	mypy civic_auth

format:
	black civic_auth tests
	ruff check --fix civic_auth tests

test:
	pytest -v --cov=civic_auth --cov-report=term-missing

build: clean
	python -m build
	twine check dist/*

clean:
	rm -rf dist/ build/ *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

publish-test: build
	twine upload --repository testpypi dist/*

publish: build
	twine upload dist/*