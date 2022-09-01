from matplotlib import pyplot as plt
import networkx as nx
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, SOSA, URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph

from viscars.namespace import DASHB

EXPECTED_PROPERTIES = [DASHB.hasProperty, DASHB.visualizedBy, DASHB.createdBy, DASHB.memberOf,
                       DASHB.produces]


def visualize_graph(graph: Graph, colored=False, save=False):
    graph_ = Graph()
    graph_ += graph.triples((None, None, None))

    users = list(graph_.subjects(RDF.type, DASHB.User))
    items = list(graph_.subjects(RDF.type, DASHB.Visualization))
    contexts = list(graph_.subjects(RDF.type, SOSA.ObservableProperty))

    graph_.remove((None, RDF.type, None))
    graph_.remove((None, RDFS.label, None))

    G = rdflib_to_networkx_multidigraph(graph_).to_undirected()

    colors = []
    for node in G.nodes():
        if URIRef(node) in users:
            colors.append('red')
        elif URIRef(node) in items:
            colors.append('green')
        elif URIRef(node) in contexts:
            colors.append('#1f78b4')
        else:
            colors.append('black')

    # Plot Networkx instance of RDF Graph
    fig = plt.figure(figsize=(16, 16))
    ax = fig.add_subplot(111)

    colors = colors if colored else None
    nx.draw(G, with_labels=False, node_color=colors, ax=ax)

    if save:
        plt.savefig('graph.png', dpi=600)
    plt.show()


def clean_graph(graph: Graph):
    G = Graph()

    for ep in EXPECTED_PROPERTIES:
        G += graph.triples((None, ep, None))

    G += graph.triples((None, RDF.type, None))

    return G
