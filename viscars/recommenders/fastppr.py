import numpy as np
from fast_pagerank import pagerank_power
import networkx as nx
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from viscars.dao import ContentRecommenderDAO, DAO, VisualizationRecommenderDAO
from viscars.recommenders.base import Recommender


class FastPersonalizedPageRank(Recommender):

    def __init__(self, dao: DAO, verbose=False, alpha=0.8, tol=10e-6):
        super().__init__(dao, verbose)

        self.alpha = alpha
        self.tolerance = tol
        self.personalization = None
        self.set_personalization(0.7, 0.3)

    def _build_model(self):
        if self.graph is not None:
            self.nx_graph = rdflib_to_networkx_multidigraph(self.graph).to_undirected()
            self.model = nx.convert_matrix.to_scipy_sparse_array(self.nx_graph)
        else:
            self.nx_graph = rdflib_to_networkx_multidigraph(self.dao.graph).to_undirected()
            self.model = nx.convert_matrix.to_scipy_sparse_array(self.nx_graph)

    def set_personalization(self, weight_uid: float = 0, weight_cid: float = 0):
        weight_others = 1 - weight_uid - weight_cid

        if weight_uid == 0:
            weight_uid = weight_others
        if weight_cid == 0:
            weight_cid = weight_others

        self.personalization = (weight_uid, weight_cid, weight_others)

    def _personalization(self, u_id, c_id):
        personalization = []

        for node in self.nx_graph.nodes:
            uri = str(node)
            if uri == u_id:
                personalization.append(self.personalization[0])
            elif uri == c_id:
                personalization.append(self.personalization[1])
            else:
                personalization.append(self.personalization[2])

        return np.array(personalization)

    def run(self, u_id: str = None, c_id: str = None):
        if u_id is not None and c_id is not None:
            weights = self._personalization(u_id, c_id)
            return pagerank_power(self.model, p=self.alpha, personalize=weights, tol=self.tolerance)

        return pagerank_power(self.model, p=self.alpha, tol=self.tolerance)

    def predict(self, u_id: str = None, c_id: str = None, **kwargs):
        ranking = self.run(u_id, c_id)
        pr = {}

        i = 0
        for node in self.nx_graph.nodes:
            pr[node] = ranking[i]
            i += 1

        recommendations = \
            [
                {'contextId': str(c_id), 'itemId': str(item), 'score': p}
                for item, p in pr.items()
                if str(item) in list(self.dao.get_items_by_context(c_id))
            ]
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, u_id: str = None, c_id: str = None, n: int = 5, **kwargs):
        pass


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../../data/protego-2/protego_ddashboard.ttl')
    graph_.parse('../../data/protego-2/protego_zplus.ttl')
    graph_.parse('../../data/protego-2/visualizations.ttl')

    # dao_ = ContentRecommenderDAO(graph_)
    #
    # recommender = FastPersonalizedPageRank(dao_)
    # recommender.set_personalization(0.3, 0.7)
    # recommendations = recommender.predict('https://dynamicdashboard.ilabt.imec.be/users/10', 'http://example.com/tx/patients/zplus_6')
    # print(recommendations)

    dao_ = VisualizationRecommenderDAO(graph_)

    recommender = FastPersonalizedPageRank(dao_)
    recommender.set_personalization(0.3, 0.7)
    recommendations = recommender.predict('https://dynamicdashboard.ilabt.imec.be/users/10', 'https://webthing.protego.dynamicdashboard.ilabt.imec.be/things/zplus_118.60%3A77%3A71%3A7D%3A93%3AD7%2Fservice0009/properties/org.dyamand.types.health.GlucoseLevel')
    print(recommendations)
