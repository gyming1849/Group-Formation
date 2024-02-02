from abc import ABC, abstractmethod
from itertools import combinations
import numpy as np


class WeightPolicy(ABC):
    @abstractmethod
    def compute(self, c, fid, el, neighbors, **kwargs):
        pass


class EuclideanWeightPolicy(WeightPolicy):
    def compute(self, c, fid, el, neighbors, **kwargs):
        if len(c):
            w = 0
            els = [el] + [neighbors[i].el for i in c]
            for el_i, el_j in combinations(els, 2):
                dist = np.linalg.norm(el_i - el_j)
                if dist == 0:
                    dist = 1e-10
                w += round(1 / dist, 4)
            return (round(w, 4),) + tuple(sorted((fid,) + c))
        return -1,
