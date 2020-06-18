import asyncio
import importlib
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Any, Callable

from pesto.ws.core.processing_error import ProcessingError

log = logging.getLogger(__name__)


async def async_exec(callback: Callable) -> Any:
    with ThreadPoolExecutor(max_workers=1) as executor:
        return await asyncio.get_event_loop().run_in_executor(executor, callback)


def load_class(path: str) -> Any:
    """
    Load a class at the provided location. Path is a string of the form: path.to.module.class and conform to the python
    import conventions.

    :param path: string pointing to the class to load
    :return: the requested class object
    """
    try:
        log.info('loading class : [{}]'.format(path))
        module_name, class_name = path.rsplit('.', 1)
        mod = importlib.import_module(module_name)
        return getattr(mod, class_name)
    except Exception:
        raise ProcessingError('Class loading error : expecting path.to.module.ClassName, got : {}'.format(path))
