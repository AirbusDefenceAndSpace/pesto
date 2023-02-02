# `pesto run` : Run the packaged algorithm

Once the processing library is built, it can be run.  
The `pesto run` command comes with 2 variants which are described below.

## pesto run docker
This variant starts the service container, calls the `process` endpoint with the provided payload and writes the 
result at the provided output location. Once done, it stops the container.

```asciidoc
Usage: pesto run docker [OPTIONS] PAYLOAD DOCKER_IMAGE OUTPUT_PATH

  (Experimental) Run a pesto algorithm in a docker. Work only for stateless
  services. Payload can be a path to a posix file or a json string

Arguments:
PAYLOAD       [required]
DOCKER_IMAGE  [required]
OUTPUT_PATH   [required]

Options:
--host-volume-path TEXT             Volume to be mounted from host
--image-volume-path TEXT            Where the volume is mounted in image
--nvidia / --no-nvidia              use nvidia runtime  [default: no-nvidia]
--ssl / --no-ssl                    run with SSL  [default: no-ssl]
--network TEXT                      Network driver to be used  [default: host]
--web-service / --no-web-service    Run the docker in WS mode, true by default. 
                                    Otherwise processing is exec in container after start  [default: web-service]
--help                              Show this message and exit.
```

Example:  
```bash
pesto run docker '{"image":"file:///opt/algo-service/pesto/tests/resources/test_1/input/image.png"}' algo-service:1.0.0.dev0 /tmp/output_pesto.json
```

If the payload references files that are not already in the image container (as in the example given), it is required
to specify host and image volume path to be mounted as parameters.

## pesto run local
This variant can be used to run the algorithm locally. It requires to have pesto, the algorithm and all its
dependencies installed at system level, which is not an easy setup.  
Alternatively, it can be used within the container image which already meet this requirement. 
The interest is then to save on the initialisation time of the container and execute several runs within the container once started.

```asciidoc
Usage: pesto run local [OPTIONS] PAYLOAD OUTPUT_PATH

  (Experimental) Run a pesto algorithm locally (not in docker). Payload can be
  a path to a posix file or a json string, or an url

Arguments:
  PAYLOAD      [required]
  OUTPUT_PATH  [required]

Options:
  --help  Show this message and exit.
```

Examples:  
Either from your local environment:
```bash
pesto run local '{"image":"file:///opt/algo-service/pesto/tests/resources/test_1/input/image.png"}' /tmp/result.txt
```

Or from inside the container that has been generated:
```bash
docker run -it --rm -v /tmp:/tmp algo-service:1.0.0.dev0 bash -c "pesto run local '{\"image\":\"file:///opt/algo-service/pesto/tests/resources/test_1/input/image.png\"}' /tmp/result.txt"```
```

## Note on SSL
The service can be started in `https` mode. For instance:
```bash
pesto run docker --ssl '{"image":"file:///opt/algo-service/pesto/tests/resources/test_1/input/image.png"}' algo-service:1.0.0.dev0 /tmp/output_pesto.json
```
or 

```bash
docker run --rm -p 4000:8080 -e PESTO_USE_SSL='1' algo-service:1.0.0.dev0
```
This should start the container so that it can be accessed from `https://localhost:4000/api/v1`

There are various ways to handle the certificates.
They should be available in the docker image as `/etc/pesto/ssl/cert.pem` and `/etc/pesto/ssl/key.pem`.


### Method 1: PESTO generated certificate
By default, some self-signed certificates are generated and deployed in the docker image under `/etc/pesto/ssl/`.
The certificate validity must be ignored in this case as it is not issued from a valid Certificate Authority.


### Method 2: self generated certificate TODO: change doc to "generic" way to generate cert (openssl, mkcert...)
You can also use your own certificate (generated with [mkcert](https://github.com/FiloSottile/mkcert) or openssl for instance).

Once generated you must make an archive of the certificate and key and declare it as a requirement.
```shell
# generate the cert and key
...
# put them in an archive for PESTO requirements
tar czf ssl.tar.gz cert.pem key.pem
```

Declare the resulting archive as a requirement in `requirements.json` (update the `from` path):
```json
{
  "environments": {
  },
  "requirements": {
    "ssl": {
      "from": "file:///path/to/your/ssl.tar.gz",
      "to": "/etc/pesto/ssl/"
    }
  },
  "dockerBaseImage": "python:3.8-buster"
}
```

### Method 3: Let's Encrypt certificate
You need to get a DNS domain registered and follow the instructions from
[Let's Encrypt](https://letsencrypt.org/getting-started/) documentation.

You can then add your key and certificate:
```shell
tar czf ssl.tar.gz cert.pem key.pem
```

Declare the resulting archive as a requirement in `requirements.json` (update the `from` path):
```json
{
  "environments": {
  },
  "requirements": {
    "ssl": {
      "from": "file:///path/to/your/ssl.tar.gz",
      "to": "/etc/pesto/ssl/"
    }
  },
  "dockerBaseImage": "python:3.8-buster"
}
```
