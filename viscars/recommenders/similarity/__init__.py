from abc import ABC, abstractmethod
import gzip
import pickle
from rdflib import Graph

from viscars.dao import DAO


class SimilarityMetric(ABC):

    def __init__(self, dao: DAO, verbose=False):
        self.verbose = verbose

        self._build_model()

    @abstractmethod
    def _build_model(self):
        pass

    @abstractmethod
    def fit(self):
        pass

    @abstractmethod
    def fit_transform(self, **kwargs):
        pass

    @abstractmethod
    def transform(self):
        pass

    def save(self, filename: str = '') -> None:
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    @staticmethod
    def load(filename: str = ''):
        with open(filename, 'rb') as f:
            metric = pickle.load(f)
            if not isinstance(metric, SimilarityMetric):
                raise ValueError(
                    'Failed to load the SimilarityMetric object'
                )
            return metric
