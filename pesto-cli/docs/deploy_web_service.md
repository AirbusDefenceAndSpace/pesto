# RestFul API Presentation

PESTO takes care of the API definition & endpoints through the [Geoprocessing API specification](https://github.com/AirbusDefenceAndSpace/geoprocessing-api/tree/master/1.0).

To learn more about RESTful API, check [this tutorial](https://www.restapitutorial.com/)


PESTO create web-services following the [OpenAPI](https://playground-docs.readthedocs.io) convention. 


## PESTO endpoints

From a user point of view, several endpoints are defined:

- `/api/v1/describe`: a GET request to get information about the packaged algorithm
- `/api/v1/health`: a GET request will send back information about the 
- `/api/v1/process`: Send the payload (contains input data) that we want to process via a POST request
- `api/v1/jobs`: a GET request to get the job list (asynchronous)
- `api/v1/jobs/{jobID}/status`: a GET request to get a job status (asynchronous)
- `api/v1/jobs/{jobID}/results`: a GET request to get a job result (asynchronous)


### **describe**
It provides a full description of the webservice : Required resources for deployment, Inputs, Outputs, Endpoints.

```bash
curl http://localhost:4000/api/v1/describe
```

!!! Example
    ```json
    {"name":"algo-service","resources":{"cpu":4,"gpu":0,"ram":8},"title":"algo-service","description":"Pesto Template contains all the boilerplate you need to create a processing-factory project","asynchronous":false,"email":"pesto@airbus.com","organization":"pesto","family":"detection","version":"1.0.0.dev0","keywords":["detection"],"template":"object-detection","config":{"$schema":"http://json-schema.org/draft-06/schema#","description":"Geo Process API config schema for algo-service","properties":{"padding":{"description":"Padding / border needed to process the tile. 0 for no padding.","maximum":256,"minimum":0,"type":"number"},"zoom":{"description":"Zoom levels that can be processed","items":{"maximum":17,"minimum":1,"type":"number"},"minItems":1,"type":"array"}},"required":["zoom","padding"],"title":"tile-object-detection-config","type":"object"},"input":{"$schema":"http://json-schema.org/draft-06/schema#","title":"","type":"object","description":"Expected format","definition":{},"definitions":{"Image":{"$schema":"http://json-schema.org/draft-06/schema#","description":"Image to process : it can be an url or the raw bytes encoded in base64","type":"string"},"Images":{"items":{"$ref":"#/definitions/Image"},"type":"array"},"Metadata":{"type":"object"},"Metadatas":{"items":{"$ref":"#/definitions/Metadata"},"type":"array"},"Polygon":{"$schema":"http://json-schema.org/draft-06/schema#","description":"GeoJSON Polygon","properties":{"bbox":{"items":{"type":"number"},"minItems":4,"type":"array"},"coordinates":{"items":{"items":{"items":{"type":"number"},"minItems":2,"type":"array"},"minItems":4,"type":"array"},"type":"array"},"type":{"enum":["Polygon"],"type":"string"}},"required":["type","coordinates"],"title":"Polygon","type":"object"},"Polygons":{"items":{"$ref":"#/definitions/Polygon"},"type":"array"}},"properties":{"dict_parameter":{"$ref":"#/definitions/Metadata","description":"A dict parameter"},"image":{"$ref":"#/definitions/Image","description":"Input image"},"integer_parameter":{"description":"A (integer) number parameter","type":"integer"},"number_parameter":{"description":"A (floating point) number parameter","type":"number"},"object_parameter":{"description":"A dict parameter with more spec, of the form {'key':'value'}","properties":{"key":{"type":"string"}},"type":"object"},"string_parameter":{"description":"A string parameter","type":"string"}},"required":["image"]},"output":{"$schema":"http://json-schema.org/draft-06/schema#","title":"","type":"object","description":"Expected format","definition":{},"definitions":{"Image":{"$schema":"http://json-schema.org/draft-06/schema#","description":"Image to process : it can be an url or the raw bytes encoded in base64","type":"string"},"Images":{"items":{"$ref":"#/definitions/Image"},"type":"array"},"Metadata":{"type":"object"},"Metadatas":{"items":{"$ref":"#/definitions/Metadata"},"type":"array"},"Polygon":{"$schema":"http://json-schema.org/draft-06/schema#","description":"GeoJSON Polygon","properties":{"bbox":{"items":{"type":"number"},"minItems":4,"type":"array"},"coordinates":{"items":{"items":{"items":{"type":"number"},"minItems":2,"type":"array"},"minItems":4,"type":"array"},"type":"array"},"type":{"enum":["Polygon"],"type":"string"}},"required":["type","coordinates"],"title":"Polygon","type":"object"},"Polygons":{"items":{"$ref":"#/definitions/Polygon"},"type":"array"}},"properties":{"areas":{"$ref":"#/definitions/Polygons"},"dict_output":{"$ref":"#/definitions/Metadata"},"geojson":{"description":"A Geojson.FeatureCollection containing only Polygons as geometries","properties":{"features":{"items":{"$schema":"http://json-schema.org/draft-06/schema#","properties":{"geometry":{"$ref":"#/definitions/Polygon"},"properties":{"oneOf":[{"type":"null"},{"type":"object"}]},"type":{"enum":["Feature"],"type":"string"}},"required":["type","properties","geometry"],"title":"GeoJSON Feature","type":"object"},"type":"array"},"type":{"type":"string"}},"type":"object"},"image":{"$ref":"#/definitions/Image"},"image_list":{"$ref":"#/definitions/Images"},"integer_output":{"type":"integer"},"number_output":{"type":"number"},"string_output":{"type":"string"}}},"_links":{"self":{"relation":"Access to describe resource","href":"http://localhost:4000/api/v1/describe","type":"application/json","method":"GET"},"execution":{"relation":"Processing resource","href":"http://localhost:4000/api/v1/process","type":"Complex type, see output in describe content for more information","method":"POST"},"config":{"relation":"Processing configuration","href":"http://localhost:4000/api/v1/config","type":"application/json","method":"GET"},"version":{"relation":"Processing version","href":"http://localhost:4000/api/v1/version","type":"application/json","method":"GET"},"health":{"relation":"Processing health","href":"http://localhost:4000/api/v1/health","type":"text/plain","method":"GET"}}}
    ```

### **health**
It provides a simple health check of the deployed web service

```bash
curl http://localhost:4000/api/v1/health
```

!!! success
    Return `OK` if the service is up and running

### **process**
It calls the processing function on provided input parameters. If asynchronous is false in the description, then the call blocks until the result is available. Otherwise, the function returns a jobid for later retrieval of the result -- [process](http://localhost:4000/api/v1/process)

[//]: # (TODO: Check and surely correct this request, which should be a POST )
```bash
curl -X POST "http://localhost:4000/api/v1/process" -d {process_payload}
```

### **Jobs list**
This endpoint returns the list of submitted job. It is available only if asynchronous is set to true in the description. 

```bash
curl http://localhost:4000/api/v1/jobs
```


### **Job status (asynchronous)**
This endpoint returns the status of a submitted job. It is available only if asynchronous is set to true in the description. 

```bash
curl http://localhost:4000/api/v1/jobs/{jobID}/status
```

### **Job result (asynchronous)**
This endpoint returns the result of a submitted job. It is available only if asynchronous is set to true in the description. 

```bash
curl http://localhost:4000/api/v1/jobs/{jobID}/results
```


## Stateful & Stateless services

PESTO supports building [stateless services as well as stateful services](https://nordicapis.com/defining-stateful-vs-stateless-web-services/).

* __Stateless__: The service replies directly to the processing request with the response. These services should have no internal state and should always return the same result when presented with the same payload

* __Stateful__: The service can have internal states, and store the processing results to be later queried.

The main difference is that sending a processing request to `api/v1/process` to a stateful service will not return the result but a `jobID`. 

The job state can be queried at `GET api/v1/jobs/{jobID}/status` and results can be queried at  `GET api/v1/jobs/{jobID}/results` when the job is done. 
The response of the latter request will be a json matching the output schema with URI to individual content (that should individually be queried using `GET requests`)

![](img/pesto_stateful.svg)

You can build the stateful service by using the [profile tool](package_docker_image.md#pesto-profiles-advanced) with:

```bash
pesto build {PESTO_PROJECT_ROOT} -p stateful
```

!!! note
    In practice, it activates the `description.stateful.json` file (already in template) which set `asynchronous` at `True`:
    ```json
    {
        "description": "My first deployment with PESTO, stateful version",
        "asynchronous": true
    }
    ```

And start the resulting stateful docker image: 

```bash
docker run --rm -p 4000:8080 {project-name}:{project-version}-stateful
```

Then, run the API usage script (`python scripts/example_api_usage.py`) while having modified the image name to stateful:

=== "Stateful"

    ```python
    service = "algo-service:1.0.0.dev0-stateful"
    ```

=== "Stateless"

    ```python
    service = "algo-service:1.0.0.dev0"
    ```

[//]: # (TODO: Test example_api_usage)

This script should send several requests (like `pesto test`), but the advantage is that it doesn't kill the service afterwards, so it is possible to look at what happened:

[//]: # (TODO: Add a request or get only those of example_api_usage?)

- Try doing a get request on `/api/v1/jobs/` you should see a list of jobs

```bash
curl "http://localhost:4000/api/v1/jobs/"
```

- Grab a job id then do a GET request on `/api/v1/jobs/{jobID}/status`. 

```bash
curl "http://localhost:4000/api/v1/jobs/{jobID}/status"
```
It should be "DONE"

- Then do a GET request on `/api/v1/jobs/{jobID}/results` to get results

```bash
curl "http://localhost:4000/api/v1/jobs/{jobID}/results"
```

It returns the result of the packaged algorithm