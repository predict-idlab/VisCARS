from enum import Enum

from viscars.recommenders.cacf import ContextAwareCollaborativeFiltering
from viscars.recommenders.cf import CollaborativeFiltering
from viscars.recommenders.fastppr import FastPersonalizedPageRank
from viscars.recommenders.mf import MatrixFactorization
from viscars.recommenders.pagerank import PageRank
from viscars.recommenders.ppr import NetworkXPersonalizedPageRank
from viscars.recommenders.random_ import RandomRank


class RecommenderType(Enum):
    """Recommender types."""
    CBCF = ('cbcf', 'context_based_collaborative_filtering')
    CF = ('cf', 'collaborative_filtering')
    FAST_PPR = ('fast_ppr', 'fast_personalized_pagerank')
    MF = ('mf', 'matrix_factorization')
    PAGERANK = ('pagerank',)
    PPR = ('ppr', 'personalized_pagerank')
    RANDOM = ('random',)

    @classmethod
    def reverse_lookup(cls, value):
        """Reverse lookup."""
        for _, member in cls.__members__.items():
            if value in member.value:
                return member
        raise LookupError


class RecommenderFactory:
    """Recommender factory."""
    types_ = {
        RecommenderType.CBCF: ContextAwareCollaborativeFiltering,
        RecommenderType.CF: CollaborativeFiltering,
        RecommenderType.FAST_PPR: FastPersonalizedPageRank,
        RecommenderType.MF: MatrixFactorization,
        RecommenderType.PAGERANK: PageRank,
        RecommenderType.PPR: NetworkXPersonalizedPageRank,
        RecommenderType.RANDOM: RandomRank,
    }

    def get(self, type_: RecommenderType):
        """
        Retrieve a recommender.

        :param type_: RecommenderType
        :return: Recommender
        """
        cls = self.types_[type_]
        return cls
