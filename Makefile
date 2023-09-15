# Makefile

# Directory where your virtual environment is located
VENV_DIR = ./venv

# Targets

.PHONY: lint
lint: pylint flake8

.PHONY: pylint
pylint:
	$(VENV_DIR)/Scripts/pylint configs mysql_db

.PHONY: isort
isort:
	$(VENV_DIR)/Scripts/isort configs mysql_db

.PHONY: flake8
flake8:
	$(VENV_DIR)/Scripts/flake8 configs mysql_db

.PHONY: black
black:
	$(VENV_DIR)/Scripts/black configs mysql_db

.PHONY: format
format: isort black

.PHONY: test
test:
	$(VENV_DIR)/Scripts/pytest

.PHONY: clean_cache
clean_cache:
	python -Bc "for p in __import__('pathlib').Path('.').rglob('*.py[co]'): p.unlink()"
	python -Bc "for p in __import__('pathlib').Path('.').rglob('__pycache__'): p.rmdir()"
	python -Bc "for p in __import__('pathlib').Path('.').rglob('*.ipynb_checkpoints'): p.rmdir()"