from abc import ABC, abstractmethod
from rdflib import Graph


class Recommender(ABC):

    def __init__(self, graph: Graph, verbose=False, **kwargs):
        self.graph = graph
        self.verbose = verbose

        self.items = []

        self._build_model()

    @abstractmethod
    def _build_model(self):
        pass

    @abstractmethod
    def predict(self, uid: [], cid: [], **kwargs):
        """

        :param uid: User ID
        :param cid: List of Context IDs
        :param n: Number of recommendations to return.
        :return: Prediction value
        """
        pass

    @abstractmethod
    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass

    def get_graph(self) -> Graph:
        return self.graph

    def set_graph(self, graph: Graph):
        self.graph = graph
        self._build_model()
