import networkx as nx
from rdflib import Graph
from rdflib.namespace import RDF
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from cars.namespace import DASHB_V1
from cars.recommenders import Recommender


class NetworkXPageRank(Recommender):

    def __init__(self, graph: Graph, verbose=False, alpha=0.8, tol=10e-6):
        super().__init__(graph, verbose)

        self.alpha = alpha
        self.tolerance = tol

    def _build_model(self):
        graph_ = Graph()
        graph_ += self.graph.triples((None, None, None))

        self.items = list(graph_.subjects(RDF.type, DASHB_V1['RealtimeDataVisualization']))
        self.model = rdflib_to_networkx_multidigraph(graph_).to_undirected()

    def set_personalization(self, weight_uid=0, weight_cid=0):
        pass

    def run(self, uid: [] = None, cid: [] = None):
        return nx.pagerank(self.model, alpha=self.alpha, tol=self.tolerance)

    def predict(self, uid: [] = None, cid: [] = None, **kwargs):
        pr = self.run(uid, cid)

        recommendations = \
            [{'contextId': cid, 'itemId': item, 'score': p} for item, p in pr.items() if item in self.items]
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass
