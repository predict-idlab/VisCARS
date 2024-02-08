import networkx as nx
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from viscars.dao import DAO, ContentRecommenderDAO
from viscars.recommenders.base import Recommender


class NetworkXPersonalizedPageRank(Recommender):

    def __init__(self, dao: DAO, verbose=False, alpha=0.8, tol=10e-6):
        super().__init__(dao, verbose)

        self.alpha = alpha
        self.tolerance = tol
        self.personalization = None
        self.set_personalization(0.3, 0.7)

    def _build_model(self):
        self.model = rdflib_to_networkx_multidigraph(self.dao.graph).to_undirected()

    def set_personalization(self, weight_uid: float = 0, weight_cid: float = 0):
        weight_others = 1 - weight_uid - weight_cid

        if weight_uid == 0:
            weight_uid = weight_others
        if weight_cid == 0:
            weight_cid = weight_others

        self.personalization = (weight_uid, weight_cid, weight_others)

    def _personalization(self, u_id, c_id):
        personalization = {}

        for node in self.model.nodes:
            uri = str(node)
            if uri in u_id:
                personalization[node] = self.personalization[0]
            elif uri in c_id:
                personalization[node] = self.personalization[1]
            else:
                personalization[node] = self.personalization[2]

        return personalization

    def run(self, u_id: [] = None, c_id: [] = None):
        if u_id is not None and c_id is not None:
            weights = self._personalization(u_id, c_id)
            return nx.pagerank(self.model, alpha=self.alpha, personalization=weights,
                               tol=self.tolerance)

        return nx.pagerank(self.model, alpha=self.alpha, tol=self.tolerance)

    def predict(self, u_id: [] = None, c_id: [] = None, **kwargs):
        pr = self.run(u_id, c_id)

        recommendations = \
            [
                {'contextId': str(c_id), 'itemId': str(item), 'score': p}
                for item, p in pr.items()
                if str(item) in list(self.dao.get_items_by_context(c_id))
            ]
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../../dao/protego/protego_ddashboard.ttl')
    graph_.parse('../../dao/protego/protego_zplus.ttl')
    graph_.parse('../../dao/protego/visualizations.ttl')

    dao_ = ContentRecommenderDAO(graph_)

    recommender = NetworkXPersonalizedPageRank(dao_)
    recommendations = recommender.predict('https://dynamicdashboard.ilabt.imec.be/users/10', 'http://example.com/tx/patients/zplus_235')
    print(recommendations)
