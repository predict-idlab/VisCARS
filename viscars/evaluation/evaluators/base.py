from viscars.dao import DAO
from viscars.recommenders.base import Recommender


class Evaluator:

    def __init__(self, dao: DAO, recommender: Recommender, metrics_: [],):
        """
        :param project_id: ID of the project (to load the correct dao).
        :param recommender: Recommender
        :param metrics_: List of Metrics
        """
        self.dao = dao
        self.recommender = recommender
        self.metrics = metrics_

    def evaluate(self):
        raise NotImplementedError
