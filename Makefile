VERSION ?= v6
PATH_TO_NOTEBOOKS ?= notebooks/$(VERSION)
PATH_TO_TESTS ?= tests/$(VERSION)

all: test

test: unit-tests notebook-tests

unit-tests:
	pytest -svx $(PATH_TO_TESTS)

notebook-tests:
	pytest --nbval --sanitize-with nbval_sanitize_file.cfg $(PATH_TO_NOTEBOOKS)

# Build distribution tarball and wheel
dist:
	mkdir -p dist/
	python setup.py sdist bdist_wheel

.PHONY: all test notebook-tests unit-tests dist
