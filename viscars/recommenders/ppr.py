import networkx as nx
import numpy as np
from rdflib import Graph
from rdflib.namespace import RDF
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from standard_api.api_handler import ApiRequester

from viscars.namespace import DASHB_V1
from viscars.recommenders import Recommender


class NetworkXPersonalizedPageRank(Recommender):

    def __init__(self, graph: Graph, verbose=False, alpha=0.8, tol=10e-6):
        super().__init__(graph, verbose)

        self.alpha = alpha
        self.tolerance = tol
        self.personalization = None

    def _build_model(self):
        graph_ = Graph()
        graph_ += self.graph.triples((None, None, None))

        self.items = list(graph_.subjects(RDF.type, DASHB_V1['RealtimeDataVisualization']))
        self.model = rdflib_to_networkx_multidigraph(graph_).to_undirected()

    def set_personalization(self, weight_uid=0, weight_cid=0):
        weight_others = 1 - weight_uid - weight_cid

        if weight_uid == 0:
            weight_uid = weight_others
        if weight_cid == 0:
            weight_cid = weight_others

        self.personalization = (weight_uid, weight_cid, weight_others)

    def _personalization(self, uid, cid):
        personalization = {}

        for node in self.model.nodes:
            uri = str(node)
            if uri in uid:
                personalization[node] = self.personalization[0]
            elif uri in cid:
                personalization[node] = self.personalization[1]
            else:
                personalization[node] = self.personalization[2]

        return personalization

    def run(self, uid: [] = None, cid: [] = None):
        if uid is not None and cid is not None:  # TODO: Check if UID and CID exist in graph -> ZeroDivisionError
            weights = self._personalization(uid, cid)
            return nx.pagerank(self.model, alpha=self.alpha, personalization=weights, tol=self.tolerance)

        return nx.pagerank(self.model, alpha=self.alpha, tol=self.tolerance)

    def get_valid_visualizations(self, properties: [], aggregation=None, from_=None, to=None):
        metadata = {
            'metadataDatabase': 'proeftuin_metadata_prod',
            'eventsDatabase': 'string'
        }
        data = {
            'propertyIds': properties,
            'aggregationId': aggregation,
            'from': from_,
            'to': to
        }

        requester = ApiRequester('https://reasoner.dynamicdashboard.ilabt.imec.be/api/v1/reasoner')
        result = requester.call('/property_visualizations', data=data, metadata=metadata)
        return [visualization['visualizationId'] for visualization in result]

    def predict(self, uid: [] = None, cid: [] = None, **kwargs):
        pr = self.run(uid, cid)

        # valid_items = self.get_valid_visualizations(cid)

        recommendations = \
            [{'contextId': cid, 'itemId': item, 'score': p} for item, p in pr.items() if item in self.items]
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass
