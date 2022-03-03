import random
from rdflib import Graph
from rdflib.namespace import RDF
from viscars.namespace import DASHB_V1
from viscars.recommenders import Recommender


class RandomRank(Recommender):

    def __init__(self, graph: Graph, verbose=False):
        super().__init__(graph, verbose)

    def _build_model(self):
        graph_ = Graph()
        graph_ += self.graph.triples((None, None, None))

        self.items = list(graph_.subjects(RDF.type, DASHB_V1['RealtimeDataVisualization']))

    def run(self, uid: [] = None, cid: [] = None):
        ranking = {}

        for i in self.items:
            ranking[i] = random.randint(0, 1)
        return ranking

    def predict(self, uid: [] = None, cid: [] = None, **kwargs):
        pr = self.run(uid, cid)

        recommendations = \
            [{'contextId': cid, 'itemId': item, 'score': p} for item, p in pr.items() if item in self.items]
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass
