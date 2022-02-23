import math

from cars.evaluation.metrics import Metric, MetricType


class Hits(Metric):
    """"Hits or True Positives."""
    type_ = MetricType.HITS

    def calculate(self, ranking, truth):
        hits = 0

        for idx, item in enumerate(ranking):
            if self.n is not None and idx >= self.n:
                break

            if item in truth:
                hits += 1

        return hits


class Precision(Metric):
    """"Precision = TP / (TP + FP)."""
    type_ = MetricType.PRECISION

    def calculate(self, ranking, truth):
        hits = Hits(self.n)

        if self.n is not None:
            ranking = ranking[:self.n]

        return hits.calculate(ranking, truth) / len(ranking)


class Recall(Metric):
    """"Recall = TP / (TP + FN)."""
    type_ = MetricType.RECALL

    def calculate(self, ranking, truth):
        hits = Hits()

        if self.n is not None:
            ranking = ranking[:self.n]

        if len(truth) == 0:
            return 0
        return hits.calculate(ranking, truth) / len(truth)


class F1(Metric):
    """"F1 = 2 * Precision * Recall / (Precision + Recall)."""
    type_ = MetricType.F1

    def calculate(self, ranking, truth):
        if self.n is not None:
            ranking = ranking[:self.n]

        precision = Precision().calculate(ranking, truth)
        recall = Recall().calculate(ranking, truth)

        if precision + recall == 0:
            return 0
        return 2 * precision * recall / (precision + recall)


class NDCG(Metric):
    """"
    Compute Normalized Discounted Cumulative Gain.

    Sum the true scores ranked in the order induced by the predicted scores, after applying a logarithmic discount.
    Then divide by the best possible score (Ideal DCG, obtained for a perfect ranking) to obtain a score between 0 and 1.
    """
    type_ = MetricType.NDCG

    def calculate(self, ranking, truth):
        dcg = 0
        idcg = self._idcg(len(truth))

        if self.n is not None:
            ranking = ranking[:self.n]

        for idx, item in enumerate(ranking):
            if item in truth:
                dcg += 1 / math.log2(idx + 2)

        if idcg == 0:
            return 0
        return dcg / idcg

    @staticmethod
    def _idcg(n):
        idcg = 0

        for i in range(n):
            idcg += 1 / math.log2(i + 2)

        return idcg
