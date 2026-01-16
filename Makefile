default: install run

run:
	python -m src.main

run-gui:
	python -m src.main_gui

install:
	pip uninstall -y moviepy && pip install --no-cache-dir --upgrade -r requirements.txt

clean:
	rm -rf dist/

lint:
	pylint src/ --fail-under=8

format:
	black src

test:
	pytest
