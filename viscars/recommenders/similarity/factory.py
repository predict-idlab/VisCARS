from enum import Enum

from viscars.recommenders.similarity.rdf2vec import RDF2VecEmbedding
from viscars.recommenders.similarity.weisfeilerlehman import WeisfeilerLehman


class SimilarityMetricType(Enum):
    """SimilarityMetric types."""
    RDF2Vec = ('rdf2vec',)
    WL = ('wl', 'weisfeiler_lehman')

    @classmethod
    def reverse_lookup(cls, value):
        """Reverse lookup."""
        for _, member in cls.__members__.items():
            if value in member.value:
                return member
        raise LookupError


class SimilarityMetricFactory:
    """SimilarityMetric factory."""
    types_ = {
        SimilarityMetricType.RDF2Vec: RDF2VecEmbedding,
        SimilarityMetricType.WL: WeisfeilerLehman
    }

    def get(self, type_: SimilarityMetricType):
        """
        Retrieve a similarity metric.

        :param type_: SimilarityMetricType
        :return: SimilarityMetric
        """
        cls = self.types_[type_]
        return cls
