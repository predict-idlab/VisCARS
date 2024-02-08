import copy
import random
from rdflib import Graph

from viscars.dao import DAO, ContentRecommenderDAO
from viscars.recommenders.base import Recommender


class CollaborativeFiltering(Recommender):
    def __init__(self, dao: DAO, verbose=False):
        super().__init__(dao, verbose)

    def _calculate_similarities(self):
        # Pearson correlation
        self.similarities = {}
        for u_id in self.dao.users['id']:
            similarities_ = {}

            items_rated_by_user = list(self.dao.ratings[self.dao.ratings['u_id'] == u_id]['i_id'])

            for n in self.dao.users:
                if u_id == n:
                    similarities_[n] = 1
                else:
                    items_rated_by_n = list(self.dao.ratings[self.dao.ratings['u_id'] == n]['i_id'])
                    common = len([i for i in items_rated_by_user if i in items_rated_by_n])
                    if common == 0:
                        similarities_[n] = 0
                    else:
                        similarities_[n] = common / len(self.dao.contexts['id'])
            self.similarities[str(u_id)] = {str(k): v for k, v in sorted(similarities_.items(), key=lambda x: x[1], reverse=True)}

    def _build_model(self):
        self._calculate_similarities()

    def knn(self, u_id, c_id, k=20, strict=True):
        similarities_ = copy.deepcopy(self.similarities)

        if u_id in similarities_[u_id].keys():
            similarities_[u_id].pop(u_id)

        return list(similarities_[u_id].items())[:k]

    def run(self, u_id, c_id, i_id, kn_neighbors=None, **kwargs):
        # Calculate K-nearest neighbours of the patient
        if kn_neighbors is None:
            kn_neighbors = self.knn(u_id, c_id, **kwargs)

        total_rw = 0
        total_w = 0
        for n, w in kn_neighbors:
            r_aui = 1 if len(list(self.dao.ratings[(self.dao.ratings['u_id'] == n) & (self.dao.ratings['i_id'] == i_id)])) > 0 else 0
            w_au = max(w, 1e-10)  # Similarity score of patient c_id and patient n
            total_rw += r_aui * w_au
            total_w += w_au
        return total_rw / total_w

    def predict(self, u_id: str, c_id: str, **kwargs):
        scores = {}

        kn_neighbors = self.knn(u_id, c_id, **kwargs)
        for iid in self.dao.get_items_by_context(c_id):
            i_id = str(iid)
            scores[i_id] = self.run(u_id, c_id, i_id, kn_neighbors=kn_neighbors, **kwargs)

        recommendations = [{'contextId': c_id, 'itemId': item, 'score': score}
                           for item, score in scores.items()]
        random.seed()
        random.shuffle(recommendations)
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../../dao/protego/protego_ddashboard.ttl')
    graph_.parse('../../dao/protego/protego_zplus.ttl')
    graph_.parse('../../dao/protego/visualizations.ttl')

    dao_ = ContentRecommenderDAO(graph_)

    recommender = CollaborativeFiltering(dao_)
    recommendations = recommender.predict('http://example.com/tx/users/daa630fe-f068-46e5-b4a8-23c92693fac5', 'http://example.com/tx/patients/zplus_6')
    print(recommendations)
