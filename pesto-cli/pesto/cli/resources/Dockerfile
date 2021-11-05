ARG ENV
FROM ${base_image}
CMD  [ "processing" ]
ENTRYPOINT []

{% if pip_config_file != None %}
{% if use_buildkit != True %}
COPY pip.conf /etc
{%  else %}
  {%  set secret_mount = secret_mount ~ ' --mount=type=secret,id=pip_config,dst=/etc/pip.conf' %}
{%  endif %}
{%  endif %}

{% if pip_extra_index != None %}
{% if use_buildkit != True %}
ARG PIP_EXTRA_INDEX_URL=${pip_extra_index}
{%  else %}
  {%  set secret_mount = secret_mount ~ ' --mount=type=secret,id=extra_index_url export PIP_EXTRA_INDEX_URL=`cat /run/secrets/extra_index_url` &&' %}
{%  endif %}
{%  endif %}

RUN python3 -V
RUN ln -s `which pip` /usr/bin/pip; echo "pip is ready"
RUN ${secret_mount} pip install --upgrade pip
RUN pip -V

RUN echo '***** fix certificates for rasterio ******************************'
    RUN ${secret_mount} pip install certifi>=2017.4.17
    RUN mkdir -p /etc/pki/tls/certs
    RUN ln -sf /etc/ssl/certs/ca-certificates.crt /etc/pki/tls/certs/ca-bundle.crt

RUN echo '***** define ENV variables ******************************'
{% for key, value in env_variables.items() -%}
    ENV ${key}=${value}
{% endfor %}

RUN echo '***** configuration files ******************************'
    COPY pesto/api_geo_process_v1.0.yaml /etc/pesto/
    COPY ${algo_name}/pesto/api/service.json /etc/pesto/
    COPY ${algo_name}/pesto/api/version.json /etc/pesto/
    COPY ${algo_name}/pesto/api/config.json /etc/pesto/

RUN echo '***** install pip requirements ******************************'
    {% for name in pip_requirements -%}
        COPY requirements/${name} /tmp
        RUN ${secret_mount} pip install /tmp/${name}
        RUN rm -rf /tmp/${name}
    {% endfor %}

RUN echo '***** copy algo resources requirements ******************************'
    {% for name, path  in resources_requirements -%}
        COPY ${name} ${path}
    {% endfor %}

RUN echo '***** install PESTO ******************************'
    COPY dist /opt/tmp/pesto/dist
    RUN ${secret_mount} if test -e /opt/tmp/pesto/dist/*.whl; then pip install /opt/tmp/pesto/dist/processing_factory*.whl; fi
    RUN ${secret_mount} if test ! -e /opt/tmp/pesto/dist/*.whl; then pip install processing-factory; fi

RUN echo '***** copy & install algorithm ******************************'
    COPY ${algo_name} /opt/${algo_name}
    RUN ${secret_mount} pip install /opt/${algo_name}
