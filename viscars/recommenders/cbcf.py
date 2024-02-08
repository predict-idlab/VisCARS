import copy
from rdflib import Graph
import time

from viscars.dao import DAO, ContentRecommenderDAO
from viscars.recommenders.base import Recommender
from viscars.recommenders.similarity.factory import SimilarityMetricType, SimilarityMetricFactory


class ContextBasedCollaborativeFiltering(Recommender):

    def __init__(self, dao: DAO,
                 similarity_metric: SimilarityMetricType = SimilarityMetricType.WL, verbose=False):
        factory = SimilarityMetricFactory()
        self.similarity_metric = factory.get(similarity_metric)(dao)

        super().__init__(dao, verbose)

    def _build_model(self):
        self.similarity_matrix = self.similarity_metric.fit_transform()
        for k, v in self.similarity_matrix.items():
            self.similarity_matrix[k] = \
                {k: v for k, v in sorted(self.similarity_matrix[k].items(), key=lambda x: x[1])}

    def knn(self, u_id, c_id, i_id, k=20, strict=True):
        similarity_matrix_ = copy.deepcopy(self.similarity_matrix)

        if c_id in similarity_matrix_[c_id].keys():
            similarity_matrix_[c_id].pop(c_id)

        filtered_neighbors = list(self.dao.ratings[self.dao.ratings['u_id'] == u_id]['c_id'])
        neighbors = list(self.similarity_matrix[c_id].items())
        kn_neighbors = []
        i = 0
        while len(kn_neighbors) < k and i < len(self.similarity_matrix):
            c, w = neighbors[i]
            if c in filtered_neighbors:
                kn_neighbors.append((c, w))

            i += 1

        return kn_neighbors

    def predict_cf(self, u_id, c_id, i_id):
        # Calculate K-nearest neighbours of the patient
        neighbours = self.knn(u_id, c_id, i_id)

        total_rw = 0
        total_w = 0
        for n, w in neighbours:
            r_aui = 1 if len(list(self.dao.ratings[(self.dao.ratings['u_id'] == n) & (self.dao.ratings['i_id'] == i_id)])) > 0 else 0
            w_au = w  # Similarity score of patient cid and patient n
            total_rw += r_aui * w_au
            total_w += w
        return total_rw / total_w if total_w > 0 else 0

    def predict(self, u_id, c_id, *kwargs):
        scores = {}
        for i_id in self.dao.get_items_by_context(c_id):
            scores[i_id] = self.predict_cf(u_id, c_id, i_id)

        recommendations = [{'contextId': c_id, 'itemId': item, 'score': score} for item, score in scores.items()]
        results = sorted(recommendations, key=lambda n: n['score'], reverse=True)
        return results

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../../dao/protego/protego_ddashboard.ttl')
    graph_.parse('../../dao/protego/protego_zplus.ttl')
    graph_.parse('../../dao/protego/visualizations.ttl')

    dao_ = ContentRecommenderDAO(graph_)

    recommender = ContextBasedCollaborativeFiltering(dao_)
    recommendations = recommender.predict('http://example.com/tx/users/daa630fe-f068-46e5-b4a8-23c92693fac5', 'http://example.com/tx/patients/zplus_6')
    print(recommendations)
