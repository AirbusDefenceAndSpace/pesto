# PESTO endpoints

PESTO create web-services following the [OpenAPI](https://playground-docs.readthedocs.io) convention. The webservice is by default available on the port 8080 (mapped to the port 4000 in the project) and offers the endpoints presented here.

You can easily launch you web service as follows : 

* `{project}/algo_service/scripts/start_service.py`

## describe
It provides a full description of the webservice : Required ressources for deployment, Inputs, Outputs, Endpoints -- [describe](http://localhost:4000/api/v1/describe).

```
http://localhost:4000/api/v1/describe
```

## process
It calls the processing function on provided input parameters. If asynchronous is false in the description, then the call blocks until the result is available. Otherwise, the function returns a jobid for later retrieval of the result -- [process](http://localhost:4000/api/v1/process)

```
http://localhost:4000/api/v1/process
```

## health
It provides a simple health check -- [health](http://localhost:4000/api/v1/health)

```
http://localhost:4000/api/v1/health
```

## Get the status of a submitted asynchronous job
This endpoint returns the status of a submitted job. It is available only if asynchronous is set to true in the description. 

```
http://localhost:4000/api/v1/jobs/{jobID}/status
```

## Get the result of a submitted asynchronous job
This endpoint returns the result of a submitted job. It is available only if asynchronous is set to true in the description. 

```
http://localhost:4000/api/v1/jobs/{jobID}/results
```


