from networkx import Graph

from cars.recommenders import Recommender


class GraphConvolutionalNetwork(Recommender):

    def __init__(self, graph: Graph, verbose=False):
        super().__init__(graph, verbose)

    def _build_model(self):
        pass

    def predict(self, uid: [], cid: [], **kwargs):
        pass

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass
