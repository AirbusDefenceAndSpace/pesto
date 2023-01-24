
## Create docker image

When your project is properly configured (cf. [project configuration](package_configuration.md)), PESTO can build a docker image containing a running web service.

If your project path is `PESTO_PROJECT_ROOT = /path/to/your/workspace/xxx-service` you can build it using :

```bash
pesto build {PESTO_PROJECT_ROOT}
```

It creates a packaged docker image:

!!! Success "xxx-service:1.0.0.dev0"


## PESTO Profiles (Advanced)


In order to accommodate for different hardware targets or slight variations of the same process to deploy, PESTO has a built-in capabilities called `profiles`.

Basically, PESTO profiles is a  list of **ordered** strings (ex: `gpu`, `stateless`) whose .json files in `build/api` folders sequentially **update** the base file.

To use them, simply add the list of profiles to your PESTO commands: 

```bash
pesto build {PESTO_PROJECT_ROOT} -p gpu stateless
```

It creates a new packaged docker image specific to the profiles:

!!! Success "xxx-service:1.0.0.dev0-stateful-gpu"


The details of profiles usage are explained in [pesto build section](pesto_build.md#profiles).


### Adding a GPU profile 

In order to create an image with GPU support, we can complete the proposed profile `gpu`.
The file `requirements.gpu.json` can be updated as follows (ex: gpu compliant pytorch image):

```json
{
  "environments": {},
  "requirements": {},
  "dockerBaseImage": "pytorch/pytorch:1.5-cuda10.1-cudnn7-runtime"
}
```

You can now build your GPU enabled microservice :

```bash
pesto build {PESTO_PROJECT_ROOT} -p gpu
```

It creates a new packaged docker image of the algorithm able to run on GPU:

!!! Success "xxx-service:1.0.0.dev0-gpu"


!!!note "Nvidia drivers"
    If you have a computer with nvidia drivers & a gpu you can try to run
    ```bash
    pesto build {PESTO_PROJECT_ROOT} -p gpu
    pesto test {PESTO_PROJECT_ROOT} -p gpu --nvidia
    ```
    It should do the same as above but with gpu support (and actually run the process on gpu).


### Multiple algorithm versions

The algorithm process is implemented in the `algorithm/process.py` with the `Process` class (see [configuration](package_configuration.md#python-algorithm)).

If multiple version of an algorithm must be maintained, it is advised to :

- Create multiple python implementation of the `Process` class (one per file)
- In the main `algorithm/process.py`, select the proper implementation of `Process` to import

The following is an example using pesto profiles to switch from one algorithm to another at build time.


!!! Example "process.py schemagen compatible, or not"

    Create `algorithm/process_v1.py`, `algorithm/process_v2.py`, `algorithm/process_v3.py`, each with it own implementation of the `Process` class.

    Use the `pesto.common.pesto.Pesto.is_profile_active()` to check the current profile (see [check profile](pesto_build.md#check-profile)).

    ```python linenums="1" title="algorithm/process.py"
    from pesto.common.pesto import Pesto

    if Pesto.is_profile_active('v1'):
        from algorithm import process_v1
        Process = process_v1.Process
    elif Pesto.is_profile_active('v2'):
        from algorithm import process_v2
        Process = process_v2.Process
    else:
        from algorithm import process_v3
        Process = process_v3.Process
    ```

    At the build time, it is possible to build one docker image per algorithm version:

    ```bash
    pesto build {PESTO_PROJECT_ROOT} -p v1
    pesto build {PESTO_PROJECT_ROOT} -p v2
    ```

    It creates the two packaged docker images of the algorithm versions:

    ```text
    xxx-service:1.0.0.dev0-v1
    xxx-service:1.0.0.dev0-v2
    ```
