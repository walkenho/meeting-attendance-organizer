ui:
	poetry run streamlit run src/maorganizer/ui.py

isort:
	./bin/run-isort.sh

flake8:
	./bin/run-flake8.sh

black:
	./bin/run-black.sh

tidy: isort black flake8

test:
	poetry run pytest

prepare: tidy test
