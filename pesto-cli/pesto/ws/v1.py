import asyncio
import logging
from typing import Any

from sanic import Blueprint, response
from sanic.exceptions import ServerError
from sanic.request import Request
from sanic.response import HTTPResponse
from sanic_openapi import doc

from pesto.ws.service.describe import DescribeService
from pesto.ws.service.job_delete import JobDeleteService
from pesto.ws.service.job_list import JobListService
from pesto.ws.service.job_result import JobResultService, ResultType
from pesto.ws.service.job_status import JobStatusService
from pesto.ws.service.process import ProcessService

log = logging.getLogger('pesto')
v1 = Blueprint('v1', url_prefix='/api/v1')

processing_semaphore = None


@v1.listener('before_server_start')
async def init(sanic, loop):
    global processing_semaphore
    processing_semaphore = asyncio.Semaphore(1, loop=loop)
    ProcessService.init()


@v1.route('/openapi')
@doc.summary('Open API specification of this service in YAML format')
async def openapi(request: Request) -> HTTPResponse:
    return await response.file('/etc/pesto/api_geo_process_v1.0.yaml')


@v1.route('/describe')
@doc.summary('Describes processing service')
@doc.produces('JSON')
async def describe(request: Request) -> HTTPResponse:
    try:
        url_root = _get_url_root(request)
        service_description = DescribeService(url_root).compute_describe()
        return response.json(service_description)
    except Exception as e:
        log.exception(e)
        raise ServerError('service.json does not exist or is not json serializable',
                          status_code=500)


@v1.route('/version')
@doc.summary('Processing version')
def version_get(request: Request) -> HTTPResponse:
    try:
        version = DescribeService.compute_version()
        return response.json(version)
    except Exception as e:
        log.exception(e)
        message = 'Could not load version file : {}'.format(DescribeService.VERSION_CONTENT_PATH)
        raise ServerError(message, status_code=500)


@v1.route('/health')
@doc.summary('Check if service is alive')
def get(request: Request) -> HTTPResponse:
    result = response.text('OK', 200)
    result.headers['content-type'] = 'text/plain'
    return result


@v1.route('/jobs', methods=['POST'])
@doc.summary('Launch process execution')
def jobs_post(request: Request) -> HTTPResponse:
    return response.redirect(request.app.url_for('api.process'))


@v1.route('/jobs', methods=['GET'])
@doc.summary('List jobs')
def jobs_get(request: Request) -> HTTPResponse:
    url_root = _get_url_root(request)
    result = JobListService().job_list(url_root)
    return response.json(result)


@v1.route('/jobs/<job_id>')
@doc.summary('Retrieve execution status')
def jobs_id_delete(request: Request, job_id: str) -> HTTPResponse:
    # Job processing is always synchronous (so no cancelling is possible)
    pass


@v1.route('/jobs/<job_id>/status')
@doc.summary('Retrieve execution status')
def jobs_id_status_get(request: Request, job_id: str) -> HTTPResponse:
    url_root = _get_url_root(request)
    status = JobStatusService(url_root, job_id).get_status()
    return response.json(status)


@v1.route('/jobs/<job_id>/results')
@doc.summary('Retrieve execution status')
def jobs_id_results_get(request: Request, job_id: str) -> HTTPResponse:
    url_root = _get_url_root(request)
    results = JobResultService(url_root, job_id).get_results()
    return response.json(results)


# @v1.route('/jobs/<job_id>/results/<result_id>', methods=['DELETE'])
@doc.summary('Retrieve execution status')
def jobs_results_delete(request: Request, job_id: str) -> HTTPResponse:
    try:
        url_root = _get_url_root(request)
        JobDeleteService(url_root, job_id).delete()
        return HTTPResponse()
    except Exception as e:
        log.exception(e)
        message = 'Error while deleting : job_id = {}'.format(job_id)
        raise ServerError(message, status_code=500)


@v1.route('/jobs/<job_id>/results/<result_id>', methods=['GET'])
@doc.summary('Retrieve execution status')
async def jobs_results_id_get(request: Request, job_id: str, result_id: str) -> HTTPResponse:
    try:
        url_root = _get_url_root(request)
        output, data_type = JobResultService(url_root, job_id).get_partial_result(result_id)
        return await _prepare_response(output, data_type)
    except Exception as e:
        log.exception(e)
        message = 'Error while retrieving results : job_id = {}, result_id = {}'.format(job_id, result_id)
        raise ServerError(message, status_code=500)


@v1.route('/jobs/<job_id>/results/<result_id>', methods=['DELETE'])
@doc.summary('Retrieve execution status')
def jobs_results_id_delete(request: Request, job_id: str, result_id: str) -> HTTPResponse:
    try:
        url_root = _get_url_root(request)
        JobDeleteService(url_root, job_id).delete_partial(result_id)
        return HTTPResponse({})
    except Exception as e:
        log.exception(e)
        message = 'Error while deleting : job_id = {}, result_id = {}'.format(job_id, result_id)
        raise ServerError(message, status_code=500)


# Implementation specifics endpoints
@v1.route('/process', methods=['POST'])
@doc.summary('Launch process execution')
async def process_post(request: Request) -> HTTPResponse:
    url_root = _get_url_root(request)
    request_payload = request.json
    if request_payload is None:
        raise ServerError('json payload is empty, or payload is not json', status_code=500)

    if processing_semaphore.locked():
        raise ServerError('a processing is already running', status_code=429)

    await processing_semaphore.acquire()
    try:
        future = ProcessService(url_root).async_process(request_payload)
        output, data_type = await asyncio.wait_for(future, timeout=None)
        return await _prepare_response(output, data_type)
    except Exception as e:
        log.exception(e)
        message = 'Error while processing, see logs for more details : {}'.format(str(e))
        raise ServerError(message, status_code=500)
    finally:
        processing_semaphore.release()


def _get_url_root(request: Request) -> str:
    return '{0.scheme}://{0.host}'.format(request)


async def _prepare_response(output: Any, data_type: ResultType):
    if data_type == ResultType.json:
        return response.json(output)
    elif data_type == ResultType.file:
        return response.text(output)
    elif data_type == ResultType.image:
        return await response.file(output)
