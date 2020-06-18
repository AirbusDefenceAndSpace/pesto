import logging

import numpy as np
import rasterio

from pesto.ws.core.pesto_feature import PestoFeature
from pesto.ws.features.converter.image.bands import FullBand, Band

log = logging.getLogger(__name__)

# TODO: Classe WIP (les méthodes expérimentales sont privées)
# Potentiellement: Revoir le rationnel / faire un travail fonctionnel
# Notamment, la gestion des ROI doit-elle être dans pesto ? => Normalement le traitement devrait recevoir des
# tuiles déjà formatées et ne pas devoir gérer le tuilage (cf spam lib etc...)
# Vérifier: Pourquoi ?


class ImageROI(object):
    def __init__(self, roi: dict):
        self.target_in = roi['target_in']
        self.target_out = roi['target_out']
        self.lines = Band(roi['lines']) if 'lines' in roi else FullBand()
        self.columns = Band(roi['columns']) if 'columns' in roi else FullBand()
        self.crop_infos = (0, 0, 0, 0)

    def compute_crop_infos(self) -> PestoFeature:
        return _ComputeCropInfos(self)

    def remove_margin(self) -> PestoFeature:
        return _RemoveMargin(self)


class DummyImageROI(ImageROI):
    """
    This class is just a placeholder to initialize pipelines when no roi is provided ...
    """

    def __init__(self):
        """
        do not call super().__init__(roi) because no roi is provided
        """
        pass

    def compute_crop_infos(self):
        return None

    def remove_margin(self):
        return None


class _ComputeCropInfos(PestoFeature):
    def __init__(self, roi: ImageROI):
        self.roi = roi

    def process(self, payload: dict) -> dict:
        self.check_payload(payload)
        for _ in self.roi.target_in:
            log.info('ROI preprocess: [{}]'.format(_))
            image_path = payload[_]
            with rasterio.open(image_path) as dataset:
                shape = dataset.shape
            top, bottom = self.roi.lines.compute_crop(shape[0])
            left, right = self.roi.columns.compute_crop(shape[1])
            self.roi.crop_infos = (top, bottom, left, right)
        return payload

    def check_payload(self, payload: dict):
        ref = None
        for _ in self.roi.target_in:
            image_path = payload[_]
            with rasterio.open(image_path) as dataset:
                shape = dataset.shape
                if ref is None:
                    ref = shape
            if shape != ref:
                raise ValueError('All images should have the same shape {} ! Wrong shape is {}'.format(ref, shape))


class _RemoveMargin(PestoFeature):
    def __init__(self, roi: ImageROI):
        self.roi = roi

    def process(self, payload: dict) -> dict:
        for x in payload:
            log.info('payload: {}'.format(x))
        top, bottom, left, right = self.roi.crop_infos

        for _ in self.roi.target_out:
            log.info('ROI postprocess: [{}]'.format(_))
            image = payload[_]
            h, w = _get_shape(image)
            payload[_] = image[..., top:h - bottom, left:w - right]
        return payload


def _get_shape(image: np.ndarray):
    if len(image.shape) == 2:
        return image.shape
    return image.shape[1:3]
