from typing import Tuple

import numpy as np


class BandInterface(object):
    def compute_crop(self, image: np.ndarray) -> Tuple[int, int]:
        raise NotImplementedError()


class Band(BandInterface):
    def __init__(self, config: dict):
        self.first = config['first']
        self.number = config['number']
        self.margin = config.get('margin', 0)
        self.last = self.first + self.number
        if self.margin < 0:
            raise ValueError('The margin must be greather than 0 : {}'.format(self.margin))

    def _check_range(self, size: int) -> None:
        last = self.first + self.number
        if not (self.first >= 0 and self.number > 0 and last <= size):
            raise ValueError('[{},{}[ are out of range for a size of {}'.format(self.first, last, size))

    def compute_crop(self, size: int) -> Tuple[int, int]:
        self._check_range(size)

        first_with_margin = max(0, self.first - self.margin)
        last_with_margin = min(size, self.last + self.margin)
        before = self.first - first_with_margin
        after = last_with_margin - self.last

        return before, after


class FullBand(BandInterface):
    def compute_crop(self, image: np.ndarray) -> Tuple[int, int]:
        return 0, 0
