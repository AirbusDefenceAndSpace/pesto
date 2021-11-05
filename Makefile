#PESTO_PYPI_PORT=7777
#PESTO_PYPI_PATH=/tmp/pesto/.pypi/
PIP=python3 -m pip
.PHONY: all build install clean uninstall test

all: install doc clean

#prepare-pypi:
#	$(PIP) install python-pypi-mirror
#	mkdir -p $(PESTO_PYPI_PATH)
#	pypi-mirror download -r pesto-cli/requirements.txt -d $(PESTO_PYPI_PATH)
#	pypi-mirror download pip -d $(PESTO_PYPI_PATH)
#
#deploy-pypi:
#	$(PIP) install pypiserver
#	mkdir -p $(PESTO_PYPI_PATH)
#	kill `lsof -t -i:$(PESTO_PYPI_PORT)` || exit 0
#	pypi-server -o -P . -a . -p $(PESTO_PYPI_PORT) $(PESTO_PYPI_PATH) &
#	export PIP_EXTRA_INDEX_URL=http://localhost:$(PESTO_PYPI_PORT)/simple/

doc:
	$(PIP) install -r .requirements.docs.txt
	cd pesto-cli &&	mkdocs build

build-whl:
	rm -rf ~/.pesto/dist/
	cd pesto-cli && python3 setup.py bdist_wheel
	mkdir -p ~/.pesto/dist/
	cp -f pesto-cli/dist/processing_factory*.whl ~/.pesto/dist/
	rm -rf pesto-cli/build

install: uninstall build-whl
	$(PIP) install ~/.pesto/dist/processing_factory*.whl

install-dev: uninstall
	cd pesto-cli && $(PIP) install -e .

deploy:
	$(PIP) install -r .requirements.docs.txt
	mkdocs gh-deploy --config-file ./pesto-cli/mkdocs.yml

clean:
	cd pesto-cli && rm -rf build dist *egg-info .eggs .pytest_cache

uninstall:
	$(PIP) uninstall processing-factory -y

test:
	rm -rf /tmp/pesto/service-template-test
	mkdir -p /tmp/pesto/service-template-test
	pesto init /tmp/pesto/service-template-test
	pesto build /tmp/pesto/service-template-test/algo-service
	pesto build /tmp/pesto/service-template-test/algo-service -p stateful
	pesto test  /tmp/pesto/service-template-test/algo-service
	pesto test  /tmp/pesto/service-template-test/algo-service -p stateful
