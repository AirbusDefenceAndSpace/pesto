import asyncio
import logging
import traceback
import uuid
from typing import Optional, Tuple, Any, Callable

from pesto.ws.core.payload_parser import PayloadParser, PestoConfig
from pesto.ws.core.pesto_feature import PestoFeatures
from pesto.ws.core.utils import load_class, async_exec
from pesto.ws.features.algorithm_wrapper import AlgorithmWrapper
from pesto.ws.features.converter.image.image_roi import ImageROI, DummyImageROI
from pesto.ws.features.payload_converter import PayloadConverter
from pesto.ws.features.payload_debug import PayloadDebug
from pesto.ws.features.response_serializer import ResponseSerializer
from pesto.ws.features.schema_validation import SchemaValidation
from pesto.ws.features.stateful_response import StatefulResponse
from pesto.ws.features.stateless_response import StatelessResponse
from pesto.ws.service.describe import DescribeService
from pesto.ws.service.job_result import ResultType

log = logging.getLogger(__name__)


class ProcessService:
    PROCESS_CLASS_NAME = 'algorithm.process.Process'

    _algorithm: Optional[Callable] = None
    _describe = None

    @staticmethod
    def init():
        if ProcessService._algorithm is not None:
            raise ValueError('Process Service already loaded !')

        try:
            log.info('ProcessService.init() ...')
            ProcessService._algorithm = load_class(ProcessService.PROCESS_CLASS_NAME)()
            if hasattr(ProcessService._algorithm, 'on_start'):
                log.info('ProcessService.on_start() ...')
                ProcessService._algorithm.on_start()
                log.info('ProcessService.on_start() ... Done !')

            log.info('ProcessService.init() ... Done !')

        except:
            traceback.print_exc()
            log.warning('Algorithm {}.on_start() failure !'.format(ProcessService.PROCESS_CLASS_NAME))

    def __init__(self, url_root: str):
        self.url_root = url_root

    @property
    def service_description(self):
        if ProcessService._describe is None:
            ProcessService._describe = DescribeService(self.url_root).compute_describe()
        return ProcessService._describe

    def process(self, payload: dict) -> dict:
        config = PayloadParser.parse(payload)

        image_roi: Optional[ImageROI] = config.get(PestoConfig.roi)  # if no ROI: None
        active_roi: ImageROI = image_roi or DummyImageROI()  # bypass compute crop info and remove margins in pipeline

        job_id = str(uuid.uuid4().time_low)

        is_stateful = self.service_description['asynchronous'] is True
        input_schema = self.service_description['input']
        output_schema = self.service_description['output']

        common_pipeline = filter(None, [
            SchemaValidation(schema=input_schema),
            active_roi.compute_crop_infos(),
            PayloadConverter(image_roi=image_roi, schema=input_schema),
            PayloadDebug(schema=input_schema),
            AlgorithmWrapper(ProcessService._algorithm),
            active_roi.remove_margin(),
            ResponseSerializer(schema=output_schema, job_id=job_id),
        ])

        if is_stateful:
            pipeline = [
                *common_pipeline,
                StatefulResponse(self.url_root, job_id)
            ]
        else:
            pipeline = [
                *common_pipeline,
                StatelessResponse(self.url_root, job_id, output_schema)
            ]

        return PestoFeatures(pipeline).process(payload)

    async def async_process(self, request_payload: dict) -> Tuple[Any, ResultType]:
        return await asyncio.wait_for(
            async_exec(lambda: self.process(request_payload)),
            timeout=None
        )
