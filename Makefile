# Basic settings
PYTHON = python
PROJECT = src/lambdora
TEST_DIR = tests

# Run all tests with coverage
test:
	pytest --cov=$(PROJECT) --cov-report=term --cov-report=html --cov-fail-under=85

# Just run tests without coverage
fasttest:
	pytest -q $(TEST_DIR)

# Generate coverage report (HTML)
coverage:
	pytest --cov=$(PROJECT) --cov-report=html

# Lint code (you can swap with flake8 or ruff)
lint:
	black --check $(PROJECT) $(TEST_DIR)

# Format code
format:
	black $(PROJECT) $(TEST_DIR)

# Clean up coverage files and build artifacts
clean:
	rm -rf .pytest_cache .coverage coverage.xml htmlcov __pycache__ */__pycache__

# Run REPL
run:
	cd src && $(PYTHON) -m lambdora.repl

# Run a file
run-file:
	cd src && $(PYTHON) -m lambdora.runner

.PHONY: test fasttest coverage lint format clean run run-file
