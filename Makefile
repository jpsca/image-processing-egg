test:
	pytest -x proper_image tests

lint:
	flake8 --config=setup.cfg proper_image tests

coverage:
	pytest --cov-report html --cov proper_image --cov tests proper_image tests

install:
	pip install -U pip wheel
	pip install -e .[dev,test]
	# pre-commit install
