# Makefile for Traffic Sign Detection project (cross-platform, Git Bash compatible)

VENV := .venv
PYTHON := $(VENV)/Scripts/python

# Commands for creating virtual environment and cleaning
CREATE_VENV := test -d $(VENV) || python -m venv $(VENV)
CLEAN_CMD_ENV := rm -rf $(VENV)
CLEAN_CMD_PYCACHE := find . -type d -name "__pycache__" -exec rm -rf {} +

.PHONY: clean run venv requirements

.DEFAULT_GOAL := run  # default target when you type "make"

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
	@echo "Installing/updating dependencies from requirements.txt..."
	@$(PYTHON) -m pip install --upgrade pip
	@$(PYTHON) -m pip install --upgrade -r requirements.txt
	@echo "Done"

# ---------------------------------------
run: requirements
	@echo "Running traffic sign detection script..."
	@$(PYTHON) znakoviDetekcija.py
	@echo "Done"
