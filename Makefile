test:
	pytest -x image_processing tests

lint:
	flake8 --config=setup.cfg image_processing tests

.PHONY: coverage
coverage:
	pytest --cov-config=pyproject.toml --cov-report html --cov image_processing image_processing tests

install:
	pip install -U pip
	pip install -e .[dev,test]
	# pre-commit install

.PHONY: types
types:
	pyright image_processing
