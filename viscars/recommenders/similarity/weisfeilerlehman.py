import grakel
from grakel.kernels import WeisfeilerLehman as WeisfeilerLehmanKernel, VertexHistogram, ShortestPath, SubgraphMatching
import json
import os
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph
from rdflib.namespace import RDF, SOSA, SSN
import time
from tqdm import tqdm

from viscars.namespace import DASHB
from viscars.recommenders.similarity import SimilarityMetric

INPUT_DIR = 'D:\\Documents\\UGent\\PhD\\projects\\PhD\\VisCARS\\data\\protego\\subgraphs'
CONTEXT_CLASS = SSN.System
USER_CLASS = DASHB.User
# ITEM_CLASS = DASHB.Visualization
ITEM_CLASS = SOSA.ObservableProperty


class WeisfeilerLehman(SimilarityMetric):

    def __init__(self, graph: Graph, verbose=False):
        super().__init__(graph, verbose)

        self._build_model()

    def _build_model(self):
        G_nx = []
        for graph_f in os.listdir(INPUT_DIR):
            if graph_f.endswith('.ttl'):
                graph = Graph()
                graph.parse(os.path.join(INPUT_DIR, graph_f), format='turtle')

                networkx_graph = rdflib_to_networkx_digraph(graph, edge_attrs=lambda s, p, o: {'label': p})
                # Add node labels
                for id_, data in networkx_graph.nodes(data=True):
                    data['label'] = id_

                G_nx.append(networkx_graph)

        self.graphs = list(grakel.utils.graph_from_networkx(G_nx, node_labels_tag='label', edge_labels_tag='label',
                                                       edge_weight_tag='weight'))

    def fit(self):
        pass

    def fit_transform(self, entity_class: str):
        contexts = set(self.graph.subjects(RDF.type, USER_CLASS))
        print(contexts)

        similarity = {}
        for idx, pid in enumerate(tqdm(contexts)):
            gk = WeisfeilerLehmanKernel(n_iter=2, normalize=True, base_graph_kernel=VertexHistogram)
            check = gk.fit_transform([self.graphs[idx]])[0]

            assert (check == 1)

            similarity[pid] = {}
            for idx_, pid_ in enumerate(contexts):
                if pid == pid_:
                    similarity[pid][pid_] = float(check)
                if pid_ in similarity.keys():
                    similarity[pid][pid_] = similarity[pid_][pid]
                else:
                    similarity[pid][pid_] = float(gk.transform([self.graphs[idx_]])[0])

        return similarity

    def transform(self):
        pass


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse(os.path.join('D:\\Documents\\UGent\\PhD\\projects\\PhD\\VisCARS\\data\\protego', 'graph.ttl'))
    rdf2vec = WeisfeilerLehman(graph_)
    distances_ = rdf2vec.fit_transform(CONTEXT_CLASS)
    print(distances_)
