# Basic settings
PYTHON = python
PROJECT = lambdora
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
	$(PYTHON) lambdora/main.py

.PHONY: test fasttest coverage lint format clean repl
