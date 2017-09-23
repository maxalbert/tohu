MODULE = tohu
CONDA_ENV_NAME ?= tohu

all: test

create-conda-environment:
	conda env create --name $(CONDA_ENV_NAME) -f environment.yml

update-conda-environment:
	conda env update --name $(CONDA_ENV_NAME) -f environment.yml

remove-conda-environment:
	conda remove --name $(CONDA_ENV_NAME) --all

test: unit-tests

unit-tests:
	py.test -svx tests/

test-notebooks:
	py.test --nbval notebooks/

.PHONY: all create-conda-environment update-conda-environment remove-conda-environment test test-notebooks unit-tests
