FROM ${base_image}
CMD  [ "processing" ]
ENTRYPOINT []

{% if pip_extra_index != None %}
ENV PIP_EXTRA_INDEX_URL=${pip_extra_index}
{%  endif %}

RUN python3 -V
RUN ln -s `which pip` /usr/bin/pip; echo "pip is ready"
RUN pip install --upgrade pip
RUN pip -V

RUN echo '***** fix certificates for rasterio ******************************'
    RUN pip install certifi>=2017.4.17
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
        RUN pip install /tmp/${name}
        RUN rm -rf /tmp/${name}
    {% endfor %}

RUN echo '***** copy algo resources requirements ******************************'
    {% for name, path  in resources_requirements -%}
        COPY ${name} ${path}
    {% endfor %}

RUN echo '***** install PESTO ******************************'
    COPY dist /opt/tmp/pesto/dist
    RUN  if test   -e /opt/tmp/pesto/dist/*.whl; then pip install /opt/tmp/pesto/dist/pesto*.whl; fi
    RUN  if test ! -e /opt/tmp/pesto/dist/*.whl; then pip install processing-factory; fi

RUN echo '***** copy & install algorithm ******************************'
    COPY ${algo_name} /opt/${algo_name}
    RUN pip install /opt/${algo_name}
