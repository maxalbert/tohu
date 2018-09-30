PATH_TO_NOTEBOOKS ?= notebooks/v4
PATH_TO_TESTS ?= tests/v4

all: test

test: unit-tests notebook-tests

unit-tests:
	pytest -svx $(PATH_TO_TESTS)

notebook-tests:
	pytest --nbval --sanitize-with nbval_sanitize_file.cfg $(PATH_TO_NOTEBOOKS)

.PHONY: all test notebook-tests unit-tests
