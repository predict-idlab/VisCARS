from viscars.data import DataLoader
from viscars.evaluation.metrics import MetricType
from viscars.evaluation.metrics.factory import MetricFactory
from viscars.recommenders import Recommender


class Evaluator:

    def __init__(self, project_id: str, recommender: Recommender, metrics_: [],):
        """
        :param project_id: ID of the project (to load the correct data).
        :param recommender: Recommender
        :param metrics_: List of Metrics
        """
        self.dLoader = DataLoader(project_id)
        self.recommender = recommender
        self.metrics = metrics_

    def evaluate(self):
        raise NotImplementedError
