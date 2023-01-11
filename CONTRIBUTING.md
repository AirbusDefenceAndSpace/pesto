# How to contribute to PESTO ?

We are following the Gitflow workflow. Stable branch is master, the active branch for development is dev. Contributions will be accepted in dev only.

To provide a patch, a new feature, report a bug or questions, please create an issue.

## Prerequisites

PESTO requires make, python 3.6, pip3, twine, git :

* `sudo apt install build-essential python3-pip twine git`

Install PESTO python package and its dependencies.
GDAL is used by the web server (inside the built docker image).

Warning: the algorithm library should not rely on any specific version of GDAL or Rasterio.

Note: For PESTO to work properly, you could need to set the following ENV variables :
- CURL_CA_BUNDLE=/etc/ssl/certs/ca-certificates.crt (behind a proxy with self signed certificate)

## Documentation

The online documentation is generated from master as follows :

```bash
make deploy
```

The documentation is available online, [Read full documentation online](https://airbusdefenceandspace.github.io/pesto).

You can also generate the documentation by yourself as follows, `make doc`. The documentation is build in pesto-cli/site/index.html.

To deploy the documentation locally and make it available on [localhost:8000/pesto](http://localhost:8000/pesto/about.html) (by default):

```bash
cd pesto-cli
mkdocs serve
```