from fast_pagerank import pagerank_power
import networkx as nx
import numpy as np
from rdflib import Graph
from rdflib.namespace import RDF
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from viscars.namespace import DASHB
from viscars.recommenders import Recommender


class FastPersonalizedPageRank(Recommender):

    def __init__(self, graph: Graph, verbose=False, alpha=0.8, tol=10e-6):
        super().__init__(graph, verbose)

        self.alpha = alpha
        self.tolerance = tol
        self.personalization = None

    def _build_model(self):
        graph_ = Graph()
        graph_ += self.graph.triples((None, None, None))

        self.items = list(graph_.subjects(RDF.type, DASHB.Visualization))

        self.nx_graph = rdflib_to_networkx_multidigraph(graph_).to_undirected()
        self.model = nx.convert_matrix.to_scipy_sparse_matrix(self.nx_graph)

    def set_personalization(self, weight_uid: float = 0.0, weight_cid: float = 0.0):
        weight_others = 1 - weight_uid - weight_cid

        if weight_uid == 0:
            weight_uid = weight_others
        if weight_cid == 0:
            weight_cid = weight_others

        self.personalization = (weight_uid, weight_cid, weight_others)

    def _personalization(self, uid, cid):
        personalization = []

        for node in self.nx_graph.nodes:
            uri = str(node)
            if uri in uid:
                personalization.append(self.personalization[0])
            elif uri in cid:
                personalization.append(self.personalization[1])
            else:
                personalization.append(self.personalization[2])

        return np.array(personalization)

    def run(self, uid: [] = None, cid: [] = None):
        if uid is not None and cid is not None:
            weights = self._personalization(uid, cid)
            return pagerank_power(self.model, p=self.alpha, personalize=weights, tol=self.tolerance)

        return pagerank_power(self.model, p=self.alpha, tol=self.tolerance)

    def predict(self, uid: [] = None, cid: [] = None, **kwargs):
        ranking = self.run(uid, cid)
        pr = {}

        i = 0
        for node in self.nx_graph.nodes:
            pr[node] = ranking[i]
            i += 1

        recommendations = \
            [{'contextId': cid, 'itemId': item, 'score': p} for item, p in pr.items() if item in self.items]
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass
