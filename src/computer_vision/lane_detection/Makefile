# Makefile for Ivina Line Detection project (cross-platform, Git Bash compatible)

VENV := .venv
PYTHON := $(VENV)/Scripts/python

# Commands for creating virtual environment and cleaning, using bash syntax
CREATE_VENV := test -d $(VENV) || python -m venv $(VENV)
CLEAN_CMD_ENV := rm -rf $(VENV)
CLEAN_CMD_PYCACHE := find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: clean run venv requirements

.DEFAULT_GOAL := run

# ---------------------------------------
clean:
	@echo "Removing __pycache__ folders..."
	@$(CLEAN_CMD_PYCACHE)
	@echo "Done"

	@echo "Removing virtual environment $(VENV) folder..."
	@$(CLEAN_CMD_ENV)
	@echo "Done"

# ---------------------------------------
venv:
	@echo "Creating virtual environment if it does not exist..."
	@$(CREATE_VENV)
	@echo "Done"

# ---------------------------------------
requirements: venv
	@echo "Installing dependencies from requirements.txt..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install -r requirements.txt
	@echo "Done"

# ---------------------------------------
run: requirements
	@echo "Running line detection script..."
	@$(PYTHON) main.py
	@echo "Done"
