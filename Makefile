test:
	pytest -x image_processing tests

lint:
	flake8 --config=setup.cfg image_processing tests

coverage:
	pytest --cov-report html --cov image_processing --cov tests image_processing tests

install:
	pip install -e .[dev,test]
	# pre-commit install

install-tests:
	pip install -e .[test]
