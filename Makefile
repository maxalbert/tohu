MODULE = randdict

all: test

test:
	py.test -sv --cov=$(MODULE) --cov-report=term-missing  .

unit-tests:
	make -C tests/unit_tests/

acceptance-tests:
	make -C tests/acceptance_tests/

update-conda-environment:
	conda env update -f environment.yml

yapf:
	@echo "Reformatting .py files using yapf"
	find . -iname "*.py" -exec yapf --style=./setup.cfg -i {} \;

clean:
	rm -rf $(MODULE)/__pycache__
	rm -rf tests/__pycache__
	rm -rf tests/unit_tests/__pycache__
	rm -rf tests/acceptance_tests/__pycache__

.PHONY: all test unit-tests acceptance-tests update-conda-environment clean

