PYLINT = /usr/bin/python3 -m pylint
ISORT = /usr/bin/python3 -m isort --check-only --recursive
PYCODESTYLE = /usr/bin/python3 -m pycodestyle
MYPY = /usr/bin/python3 -m mypy

lint:
	$(PYLINT) *py
	$(PYCODESTYLE) *py
	$(ISORT) *py
	$(MYPY) *py
