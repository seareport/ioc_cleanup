.PHONY: list docs

list:
	@LC_ALL=C $(MAKE) -pRrq -f $(lastword $(MAKEFILE_LIST)) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | grep -E -v -e '^[^[:alnum:]]' -e '^$@$$'

init:
	poetry install --sync --with dev
	pre-commit install

style:
	pre-commit run ruff-format -a

lint:
	pre-commit run ruff -a

mypy:
	dmypy run ioc_cleanup

test:
	python -m pytest -vlx

cov:
	coverage erase
	python -WError -m pytest --cov=ioc_cleanup --cov-report term-missing --durations=10 --pdb

deps:
	pre-commit run poetry-lock -a
	pre-commit run poetry-check -a
	pre-commit run poetry-export -a
