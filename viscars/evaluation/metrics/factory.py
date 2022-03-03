from viscars.evaluation.metrics import MetricType
from viscars.evaluation.metrics.metrics import Hits, Precision, Recall, F1, NDCG


class MetricFactory:
    """Evaluation metric factory."""
    types_ = {
        MetricType.HITS: Hits,
        MetricType.PRECISION: Precision,
        MetricType.RECALL: Recall,
        MetricType.F1: F1,
        MetricType.NDCG: NDCG
    }

    def get(self, type_: MetricType, n=None):
        """
        Retrieve a metric.

        :param type_: MetricType
        :param n: Top N
        :return: Metric
        """
        cls = self.types_[type_]
        return cls(n)
