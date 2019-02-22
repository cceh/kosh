.PHONY: clean install
.SILENT: clean install
default: clean install

clean:
	rm -fr \
		__pycache__ \
		build \
		dist \
		kosh.egg-info \
		kosh/docs/*.html

install:
	pip3 install -r requirements.txt
	(cd kosh/docs && pydoc3 -w ../..)
	python3 setup.py install
