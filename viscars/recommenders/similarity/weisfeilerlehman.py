import grakel
from grakel.kernels import WeisfeilerLehman, VertexHistogram, ShortestPath, SubgraphMatching
import os
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

G_nx = []
pid = []
for graph_f in os.listdir(base_dir):
    if graph_f.endswith('.ttl'):
        graph = Graph()
        graph.parse(os.path.join(base_dir, graph_f), format='turtle')

        networkx_graph = rdflib_to_networkx_multidigraph(graph)
        G_nx.append(networkx_graph)
        pid.append(graph_f.split('.')[0])

graphs = list(grakel.utils.graph_from_networkx(G_nx))
