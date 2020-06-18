import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from sanic import Sanic
from sanic import response
from sanic.exceptions import ServerError

model = None


def processing():
    global model
    if not model:
        model = 'xxxx'
        print('loading model')

    print("start processing")
    for i in range(10):
        time.sleep(1)
        print(i)
    return {"processing": "result"}


app = Sanic()

processing_semaphore = None


@app.listener('before_server_start')
async def init(sanic, loop):
    global processing_semaphore
    processing_semaphore = asyncio.Semaphore(1, loop=loop)


async def async_exec(callback):
    with ThreadPoolExecutor(max_workers=1) as executor:
        return await asyncio.get_event_loop().run_in_executor(executor, callback)


@app.route("/process")
async def process(request):
    if processing_semaphore.locked():
        raise ServerError('a processing is already running', status_code=423)

    await processing_semaphore.acquire()
    try:
        future = async_exec(processing)
        result = await asyncio.wait_for(future, timeout=None)
        return response.json(result)
    finally:
        processing_semaphore.release()


@app.route("/health")
async def health(request):
    return response.json({"health": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4000)
