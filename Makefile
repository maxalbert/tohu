MODULE = tohu
CONDA_ENV_NAME ?= tohu

all: test

test: unit-tests

unit-tests:
	pytest -svx tests/

notebooks-tests:
	pytest --nbval notebooks/

.PHONY: all test notebooks-tests unit-tests
