import asyncio
import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, Response, RedirectResponse, FileResponse

from pesto.ws.service.describe import DescribeService
from pesto.ws.service.job_delete import JobDeleteService
from pesto.ws.service.job_list import JobListService
from pesto.ws.service.job_result import JobResultService, ResultType
from pesto.ws.service.job_status import JobStatusService
from pesto.ws.service.process import ProcessService

log = logging.getLogger('pesto')
v1 = APIRouter(
    prefix='/api/v1',
    tags=['v1'],
    responses={404: {'description': 'Not found'}}
)

processing_semaphore = None

@v1.on_event('startup')
async def startup_event():
    global processing_semaphore
    processing_semaphore = asyncio.Semaphore(1)
    ProcessService.init()

#TODO : remplacer par le download du JSON spécifique
@v1.get('/openapi')
def openapi(request: Request) -> FileResponse:
    return FileResponse('/etc/pesto/api_geo_process_v1.0.yaml')

#TODO : Create a model of response for describe
@v1.get('/describe')
async def describe(request: Request) -> JSONResponse:
    try:
        url_root = _get_url_root(request)
        service_description = DescribeService(url_root).compute_describe()
        return JSONResponse(content=service_description)
    except Exception as e:
        log.exception(e)
        raise HTTPException(detail='service.json does not exist or is not json serializable',
                          status_code=500)

@v1.get('/version')
def version_get(request: Request) -> JSONResponse:
    try:
        version = DescribeService.compute_version()
        return JSONResponse(content=version)
    except Exception as e:
        log.exception(e)
        message = 'Could not load version file : {}'.format(DescribeService.VERSION_CONTENT_PATH)
        raise HTTPException(detail=message, status_code=500)


@v1.get('/health')
def health() -> Response:
    return Response(content='OK',status_code=200,media_type='text/plain')

@v1.post('/jobs')
def jobs_post(request: Request) -> JSONResponse:
    return RedirectResponse(request.app.url_for('api.process'))

@v1.get('/jobs')
def jobs_get(request: Request) -> JSONResponse:
    url_root = _get_url_root(request)
    result = JobListService().job_list(url_root)
    return JSONResponse(content=result)

@v1.get('/jobs/{job_id}/status')
def jobs_id_status_get(request: Request, job_id: str) -> JSONResponse:
    url_root = _get_url_root(request)
    status = JobStatusService(url_root, job_id).get_status()
    return JSONResponse(content=status)

@v1.get('/jobs/{job_id}/results')
def jobs_id_results_get(request: Request, job_id: str) -> JSONResponse:
    url_root = _get_url_root(request)
    results = JobResultService(url_root, job_id).get_results()
    return JSONResponse(content=results)

@v1.get('/jobs/{job_id}/results/{result_id}')
async def jobs_results_id_get(request: Request, job_id: str, result_id: str) -> JSONResponse:
    try:
        url_root = _get_url_root(request)
        output, data_type = JobResultService(url_root, job_id).get_partial_result(result_id)
        return await _prepare_response(output, data_type)
    except Exception as e:
        log.exception(e)
        message = 'Error while retrieving results : job_id = {}, result_id = {}'.format(job_id, result_id)
        raise HTTPException(detail=message, status_code=500)

@v1.delete('/jobs/{job_id}/results/{result_id}')
def jobs_results_id_delete(request: Request, job_id: str, result_id: str) -> JSONResponse:
    try:
        url_root = _get_url_root(request)
        JobDeleteService(url_root, job_id).delete_partial(result_id)
        return JSONResponse({})
    except Exception as e:
        log.exception(e)
        message = 'Error while deleting : job_id = {}, result_id = {}'.format(job_id, result_id)
        raise HTTPException(detail=message, status_code=500)


# Implementation specifics endpoints
@v1.post('/process')
async def process_post(request: Request) -> JSONResponse:
    url_root = _get_url_root(request)
    request_payload = await request.json()
    if request_payload is None:
        raise HTTPException(detail='json payload is empty, or payload is not json', status_code=500)

    if processing_semaphore.locked():
        raise HTTPException(detail='a processing is already running', status_code=429)

    await processing_semaphore.acquire()
    try:
        future = ProcessService(url_root).async_process(request_payload)
        output, data_type = await asyncio.wait_for(future, timeout=None)
        return await _prepare_response(output, data_type)
    except Exception as e:
        log.exception(e)
        message = 'Error while processing, see logs for more details : {}'.format(str(e))
        raise HTTPException(detail=message, status_code=500)
    finally:
        processing_semaphore.release()


def _get_url_root(request: Request) -> str:
    return '{}://{}:{}'.format(request.url.scheme,request.url.hostname,request.url.port)


async def _prepare_response(output: Any, data_type: ResultType):
    if data_type == ResultType.json:
        return JSONResponse(content=output)
    elif data_type == ResultType.file:
        return Response(content=output,status_code=200,media_type='text/plain')
    elif data_type == ResultType.image:
        with open(output, "rb") as f:
            image = f.read()
        return Response(content=image, media_type="image/png")
