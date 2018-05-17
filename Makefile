MODULE = tohu
CONDA_ENV_NAME ?= tohu

all: test

test: unit-tests

unit-tests:
	pytest -svx tests/

test-notebooks:
	pytest --nbval notebooks/

.PHONY: all test test-notebooks unit-tests
