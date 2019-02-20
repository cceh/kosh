.PHONY: clean install
.SILENT: clean install
default: clean install

clean:
	pip3 uninstall -y kosh
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
