# Thin wrapper. The real logic is scripts/site.py so Windows without make works too.
PY ?= python3
.PHONY: fetch check build validate verify release clean
fetch check build validate verify release:
	$(PY) scripts/site.py $@
clean:
	$(PY) -c "import shutil; shutil.rmtree('dist', ignore_errors=True)"
