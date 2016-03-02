MODULE = randdict
CONDA_ENV_NAME ?= randdict

all: test

test:
	py.test -sv --cov=$(MODULE) --cov-report=term-missing  .

unit-tests:
	make -C tests/unit_tests/

acceptance-tests:
	make -C tests/acceptance_tests/

create-conda-environment:
	conda env create --name $(CONDA_ENV_NAME) -f environment.yml

update-conda-environment:
	conda env update --name $(CONDA_ENV_NAME) -f environment.yml

remove-conda-environment:
	conda remove --name $(CONDA_ENV_NAME) --all

yapf:
	@echo "Reformatting .py files using yapf"
	find . -iname "*.py" -exec yapf --style=./setup.cfg -i {} \;

clean:
	rm -rf $(MODULE)/__pycache__
	rm -rf tests/__pycache__
	rm -rf tests/unit_tests/__pycache__
	rm -rf tests/acceptance_tests/__pycache__

.PHONY: all test unit-tests acceptance-tests create-conda-environment update-conda-environment remove-conda-environment clean

