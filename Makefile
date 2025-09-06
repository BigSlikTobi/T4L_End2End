.PHONY: install lint format test alembic-init

install:
	python -m pip install -U pip
	pip install -e .[dev]

lint:
	black --check .
	isort --check-only .
	flake8
	mypy src

format:
	black .
	isort .

test:
	pytest

alembic-init:
	alembic revision -m "init" --autogenerate
