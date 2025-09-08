.PHONY: install lint format test alembic-init migrate

install:
	python -m pip install -U pip
	pip install -e .[dev]

verify-nfl:
	@python - <<'PY'
try:
	import importlib
	import sys
	import pkgutil
	ok = pkgutil.find_loader('nfl_data_py') is not None
	print({"nfl_data_py": {"available": ok}})
except Exception as e:
	print({"nfl_data_py": {"available": False, "error": str(e)}})
	sys.exit(0)
PY

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

migrate:
	python -m src.database.init_db
