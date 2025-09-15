# Makefile for JSON Diffing Project

.PHONY: help install test test-coverage lint format clean setup-hooks run-diff run-reconstruct

# Default target
help:
	@echo "Available targets:"
	@echo "  install        - Install dependencies"
	@echo "  test           - Run all tests"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo "  lint           - Run linting checks"
	@echo "  format         - Format code with black"
	@echo "  clean          - Clean up temporary files"
	@echo "  setup-hooks    - Set up pre-commit hooks"
	@echo "  run-diff       - Run json_diff.py with sample files"
	@echo "  run-reconstruct - Run json_reconstructor.py with sample files"

# Install dependencies
install:
	pip3 install -r requirements.txt

# Run all tests
test:
	python3 -m pytest test_*.py -v

# Run tests with coverage
test-coverage:
	python3 -m pytest test_*.py --cov=json_diff --cov=json_reconstructor --cov-report=html --cov-report=term

# Run linting
lint:
	flake8 *.py
	black --check *.py

# Format code
format:
	black *.py

# Clean up temporary files
clean:
	rm -f diff_export.json
	rm -f test_reconstructed.json
	rm -f reconstructed_*.json
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete

# Set up pre-commit hooks
setup-hooks:
	pip3 install pre-commit
	pre-commit install

# Run json_diff.py with sample files
run-diff:
	python3 json_diff.py zuora_workflow1.json zuora_workflow2.json

# Run json_reconstructor.py with sample files
run-reconstruct:
	python3 json_reconstructor.py zuora_workflow1.json diff_export.json reconstructed_test.json

# Development workflow
dev-setup: install setup-hooks
	@echo "Development environment set up successfully!"

# Full test suite
full-test: lint test test-coverage
	@echo "All tests passed!"

# Quick validation
validate: format lint test
	@echo "Validation complete!"
