# Run the pesto docker image

If the build succeeds you should be able to see your image with the following command

```bash
docker image ls
```

!!! success
    ```
    REPOSITORY                                                  TAG          IMAGE ID       CREATED         SIZE
    algo-service                                                1.0.0.dev0   f04d96bb57f4   4 minutes ago   1.16GB
    ```

There are different ways to run the docker image of your algorithm created with `pesto build`.


- ## pesto run docker

```bash
pesto run docker '{"image":"file:///opt/algo-service/pesto/tests/resources/test_1/input/image.png"}' algo-service:1.0.0.dev0 /tmp/output_pesto.json
```

- ## pesto run local

[//]: # (TODO: Add pesto run docker local command)

- ## docker run

You can start a container with you packaged algorithm docker image directly with docker command:

```bash
docker run --rm -p 4000:8080 algo-service:1.0.0.dev0
```

This should start the container so that it can be accessed from `http://localhost:4000`.


- ## start service

You can also launch your web service as follows : 

```bash
$ python {PESTO_PROJECT_ROOT}/algo_service/scripts/start_service.py
```

The webservice is by default available on the port 8080 (mapped to the port 4000 in the project) and offers the [PESTO endpoints](deploy_web_service.md#pesto-endpoints).
