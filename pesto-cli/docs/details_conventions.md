# Conventions: using PESTO properly


## Image format (numpy array)

For image processing solutions, PESTO offers mechanisms to indifferently feed algorithms with images as hyperlinks (either on a web server, on the disk, or in a GCP storage) or base64 encoded data as far as the [Image type](package_configuration.md#input--output-specification) is used.
For that purpose, [raster.io](https://rasterio.readthedocs.io/en/latest/) is used.

PESTO decodes input request in a specific way, which means that for images they are provided to the algorithm in Channel,Height,Width format, 
PESTO is based on numpy arrays to send to or receive from the packaged algorithm.
The convention is to encode images as arrays with 3 dimensions `(C,H,W)` :

- C is the channel number
- H is the lines number
- W is the columns number

For example, an RGBA image of dimension 256x256 should be encoded as a numpy array of shape (4,256,256).

!!! warning
    The usual format for images is `(H,W,C)`. 
    This means that a transposition is required to wrap them up in PIL format for example.

!!! tip 
    With `image` as a `np.array`, the easiest way to do so is to call `image = image.transpose((1, 2, 0))` to reorder bands



## Delivery name convention

Given a `build.json` file :
```json
{
  "name": "service-xxx",
  "version": "a.b.c"
}
```

and the build command :
```bash
pesto build build.json -p p1 p2
```

The packaged docker image is automatically named :
```
service-xxx:a.b.c-p1-p2
```

## Docker image naming

Docker images naming convention is : 

* `{ service-name }:{version}` when no profile is used
* `{ service-name }:{version}-stateful` when no profile is used and the service is asynchronous.
* `{ service-name }:{version}-{profile}` when a profile is specified
* `{ service-name }:{version}-{profile}-stateful` when a profile is specified and the service is asynchronous.

## PESTO internal workspaces

Pesto uses workspaces for building services and storing partial responses in asynchronous mode.
Finally, automatic testing copy resources (images) to a temporary folder.
Here is a description of the paths where PESTO could write some files :

```
pesto-cli build :                           $HOME/.pesto/service-name/x.y.z/
pesto-cli build requirements (local cache): $HOME/.pesto/.processing-factory-requirements/
pesto-ws async jobs files :                 $HOME/.pesto/.processing/jobs/${job_id}/
pesto-template (unit testing) :             /tmp/pesto/test
```
