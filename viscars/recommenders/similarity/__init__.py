from abc import ABC, abstractmethod
import gzip
import pickle


class SimilarityMetric(ABC):

    def __init__(self, graph, verbose=False):
        self.graph = graph
        self.verbose = verbose

        self.data = dict()

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
