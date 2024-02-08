from abc import ABC, abstractmethod

from rdflib import Graph

from viscars.dao import DAO


class Recommender(ABC):

    def __init__(self, dao: DAO, verbose=False, **kwargs):
        self.dao = dao
        self.verbose = verbose

        self.items = []

        self._build_model()

    @abstractmethod
    def _build_model(self):
        pass

    @abstractmethod
    def predict(self, u_id: [], c_id: [], **kwargs):
        """

        :param u_id: User ID
        :param c_id: List of Context IDs
        :return: Prediction value
        """
        pass

    @abstractmethod
    def top_n(self, u_id: [], c_id: [], n, **kwargs):
        pass

    def get_graph(self) -> Graph:
        return self.graph

    def set_graph(self, graph: Graph):
        self.graph = graph
        self._build_model()

