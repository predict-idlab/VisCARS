from enum import Enum

from cars.recommenders.fastppr import FastPersonalizedPageRank
from cars.recommenders.pagerank import NetworkXPageRank
from cars.recommenders.ppr import NetworkXPersonalizedPageRank
from cars.recommenders.random import RandomRank


class RecommenderType(Enum):
    """Metric types."""
    PAGERANK = 'pagerank'
    PPR = 'ppr'
    FAST_PPR = 'fast_ppr'
    RANDOM = 'random'

    @classmethod
    def reverse_lookup(cls, value):
        """Reverse lookup."""
        for _, member in cls.__members__.items():
            if member.value == value:
                return member
        raise LookupError


class RecommenderFactory:
    """Recommender factory."""
    types_ = {
        RecommenderType.PAGERANK: NetworkXPageRank,
        RecommenderType.PPR: NetworkXPersonalizedPageRank,
        RecommenderType.FAST_PPR: FastPersonalizedPageRank,
        RecommenderType.RANDOM: RandomRank,
    }

    def get(self, type_: RecommenderType):
        """
        Retrieve a recommender.

        :param type_: RecommenderType
        :return: Metric
        """
        cls = self.types_[type_]
        return cls
