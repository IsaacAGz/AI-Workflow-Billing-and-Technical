VENV_PY = venv/Scripts/python
PIP = venv/Scripts/pip

.PHONY: setup install run clean

setup:
	python -m venv venv
	$(VENV_PY) -m pip install --upgrade pip
	$(PIP) install -r requirements.txt

install:
	$(PIP) install -r requirements.txt

run:
	$(VENV_PY) src/main.py

clean:
	rm -rf venv
	find . -type d -name "__pycache__" -exec rm -rf {} +