
## Create docker image

When your project is properly configured (cf. [project configuration](package_configuration.md)), PESTO can build a docker image containing a running web service.

If your project path is `PESTO_PROJECT_ROOT = /path/to/your/workspace/xxx-service` you can build it using :

```bash
pesto build {PESTO_PROJECT_ROOT}
```

## PESTO Profiles (Advanced)


In order to accommodate for different hardware targets or slight variations of the same process to deploy, PESTO has a built-in capabilities called `profiles`.

Basically, PESTO profiles is a  list of **ordered** strings (ex: `gpu`, `stateless`) whose .json files in `build/api` folders sequentially **update** the base file.

To use them, simply add the list of profiles to your PESTO commands: 

```bash
pesto build {PESTO_PROJECT_ROOT} -p gpu stateless
```

The details of profiles usage are explained in [pesto build section](pesto_build.md#profiles).


### Multiple algorithm versions

If multiple version of an algorithm must be maintained, it is advised to :

- Create multiple python implementation of the `Process` class (one per file)
- Use the `pesto.common.pesto.Pesto.is_profile_active()` to check the current profile (see [check profile](pesto_build.md#check-profile))
- Select the proper implementation of `Process` to import

The following is an example using pesto profiles to switch from one algorithm to another at build time.

```python
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

The `Process` corresponding to the desired profile is then used in the rest of the algorithm run.

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

!!!note "Nvidia drivers"
    If you have a computer with nvidia drivers & a gpu you can try to run
    ```bash
    pesto build {PESTO_PROJECT_ROOT} -p gpu
    pesto test {PESTO_PROJECT_ROOT} -p gpu --nvidia
    ```
    It which should do the same as above but with gpu support (and actually run the process on gpu).

[//]: # (TODO: test if nvidia is still available)
