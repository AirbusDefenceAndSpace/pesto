
# Change Log

## 1.7.2
- Removed misleading error message at run time, when process does not use Input/Output classes
- Added message to clarify that not importing Input/Output remains nominal (legacy behaviour).
- Updated makefile to enable github action for deploying online documentation.
## 1.7.1
- HTTPS Activation with PESTO_USE_SSL use true or false values
- automatic documentation publishing

## 1.7.0
- HTTPS support

## 1.6.0
- Significant documentation update : updates (tutorial, pesto commands), new sections (contributing, running pesto, ), new documentation organisation and a new skin.

## 1.5.0
- PESTO provides an automatic schema generation: generation of the input & output json schemas based on the signature of the process function
- Cache for pesto build: a faster docker image build with different cache levels

## 1.4.0
- PESTO CLI now uses Typer to reduce code base
- Add run commands to CLI to run processing (locally or in docker image) with pesto run

## 1.3.3
- Fix response when output is an image

## 1.3.2
- Fix missing hostname in URL in describe (API change between Sanic & FastAPI)

## 1.3.1
- Fix wrong access in log dict
- Add extra field for log

## 1.3.0
- Move from Sanic to FastAPI
- Log based on Loguru
- Fix test procedure un Makefile

## 1.2.2 - 2021-06-17
- Fix potential memory leak in the web service

## 1.2.1 - 2021-06-08
- Fix wrong wheel name in Dockerfile

## 1.2.1 - 2021-06-08
- Fix wrong wheel name in Dockerfile

## 1.2.0 - 2021-04-08
- Change the package name from `pesto-cli` to `processing-factory`

## 1.1.0 - 2021-04-06
- Append `PYTHONPATH` during `pesto build` instead of overwriting.
- Add `--network` command line option to `pesto build` and `pesto test`.

## 1.0.0 - 2020-06-18
- First release of PESTO.
