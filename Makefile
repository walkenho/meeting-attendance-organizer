ui:
	poetry run streamlit run ui.py


isort:
	./bin/run-isort.sh

flake8:
	./bin/run-flake8.sh

black:
	./bin/run-black.sh

test:
	poetry run pytest

prepare: isort black flake8 test
