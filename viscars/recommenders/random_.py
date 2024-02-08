import random
from rdflib import Graph

from viscars.dao import DAO, ContentRecommenderDAO
from viscars.recommenders.base import Recommender


class RandomRank(Recommender):

    def __init__(self, dao: DAO, verbose=False):
        super().__init__(dao, verbose)

    def _build_model(self):
        pass

    def predict(self, u_id: str = None, c_id: str = None, **kwargs):
        scores = {item: float(random.randint(0, 10000)) / 10000 for item in self.dao.get_items_by_context(c_id)}
        recommendations = \
            [{'contextId': str(c_id), 'itemId': str(item), 'score': p} for item, p in scores.items()]
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../../dao/protego/protego_ddashboard.ttl')
    graph_.parse('../../dao/protego/protego_zplus.ttl')
    graph_.parse('../../dao/protego/visualizations.ttl')

    dao_ = ContentRecommenderDAO(graph_)

    recommender = RandomRank(dao_)
    recommendations = recommender.predict('https://dynamicdashboard.ilabt.imec.be/users/10', 'http://example.com/tx/patients/zplus_6')
    print(recommendations)
