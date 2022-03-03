"""Evaluation metrics."""
from abc import ABC, abstractmethod
from enum import Enum


class MetricType(Enum):
    """Metric types."""
    HITS = 'hits'
    PRECISION = 'precision'
    RECALL = 'recall'
    F1 = 'f1'
    NDCG = 'ndcg'

    @classmethod
    def reverse_lookup(cls, value):
        """Reverse lookup."""
        for _, member in cls.__members__.items():
            if member.value == value:
                return member
        raise LookupError


class Metric(ABC):
    type_ = None

    def __init__(self, n=None):
        self.n = n

    @abstractmethod
    def calculate(self, ranking, truth):
        pass

    def __str__(self):
        name = self.type_.value
        return f'{name}@{self.n}' if self.n is not None else name