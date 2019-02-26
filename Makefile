PY_SOURCES= $(wildcard **/*.py) $(wildcard */*/*.py)

lint: $(PY_SOURCES)
	pylint -E $?

