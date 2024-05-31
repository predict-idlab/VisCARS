from abc import ABC, abstractmethod
import logging
from rdflib import Graph

from viscars.dao import DAO


class Recommender(ABC):

    def __init__(self, dao: DAO, verbose=False, **kwargs):
        self.dao = dao
        self.graph = self.dao.get_graph()
        self.verbose = verbose

        self.items = []

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)
        formatter = logging.Formatter('[%(asctime)s] - [%(name)s] - [%(levelname)s] %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

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

