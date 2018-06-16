MODULE = tohu
CONDA_ENV_NAME ?= tohu

all: test

test: unit-tests notebook-tests

unit-tests:
	pytest -svx tests/

notebook-tests:
	pytest --nbval notebooks/

.PHONY: all test notebook-tests unit-tests
