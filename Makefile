# Basic settings
PYTHON = python3
PROJECT = src/lambdora
TEST_DIR = tests

# Run all tests with coverage
test:
	$(PYTHON) -m pytest --cov=$(PROJECT) --cov-report=term --cov-report=html --cov-report=xml --cov-fail-under=85

# Just run tests without coverage
fasttest:
	$(PYTHON) -m pytest -q $(TEST_DIR)

# Generate coverage report (HTML)
coverage:
	$(PYTHON) -m pytest --cov=$(PROJECT) --cov-report=html

# Lint code
lint:
	$(PYTHON) -m ruff check --fix $(PROJECT)

# Format code
format:
	$(PYTHON) -m black $(PROJECT)

# Clean up coverage files, build artifacts, and REPL history
clean:
	$(PYTHON) scripts/clean.py

# Install package in editable mode
install:
	$(PYTHON) -m pip install -e .

# Run REPL
run:
	cd src && $(PYTHON) -m lambdora.repl

# Run a file
run-file:
	cd src && $(PYTHON) -m lambdora.runner

# Install dev dependencies (pytest, coverage, ruff, black)
install-dev:
	$(PYTHON) -m pip install -e .[dev]

.PHONY: test fasttest coverage lint format clean install run run-file install-dev
