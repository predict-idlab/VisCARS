from fast_pagerank import pagerank_power
import networkx as nx
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from viscars.dao import DAO, ContentRecommenderDAO
from viscars.recommenders.base import Recommender


class PageRank(Recommender):

    def __init__(self, dao: DAO, verbose=False, alpha=0.8, tol=10e-6):
        super().__init__(dao, verbose)

        self.alpha = alpha
        self.tolerance = tol

    def _build_model(self):
        self.nx_graph = rdflib_to_networkx_multidigraph(self.dao.graph).to_undirected()
        self.model = nx.convert_matrix.to_scipy_sparse_matrix(self.nx_graph)

    def run(self, u_id: str = None, c_id: str = None):
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
    graph_.parse('../../dao/protego/protego_ddashboard.ttl')
    graph_.parse('../../dao/protego/protego_zplus.ttl')
    graph_.parse('../../dao/protego/visualizations.ttl')

    dao_ = ContentRecommenderDAO(graph_)

    recommender = PageRank(dao_)
    recommendations = recommender.predict('https://dynamicdashboard.ilabt.imec.be/users/10', 'http://example.com/tx/patients/zplus_235')
    print(recommendations)
