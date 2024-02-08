from matplotlib import pyplot as plt
import networkx as nx
from rdflib import Graph
from rdflib.namespace import RDF, RDFS, SOSA, URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
from rdflib.term import Node
from typing import Dict

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


def extract_sub_graph_from_rdf_graph(graph: Graph, instance: Node or str) -> Graph:
    if type(instance) == str:
        instance = URIRef(instance)
    walks = [[(s, p, o)] for s, p, o in graph.triples((instance, None, None))]
    walks_ = []

    while walks:
        for walk in walks.copy():
            s, p, o = walk[-1]

            is_endpoint = True
            for s_, p_, o_ in graph.triples((o, None, None)):
                if o_ not in [hop[0] for hop in walk]:  # Early stopping (circular walks)
                    walk_ = walk.copy()
                    walk_.append((s_, p_, o_))
                    walks.append(walk_)
                    is_endpoint = False

            if is_endpoint:
                walks_.append(walk)
            walks.remove(walk)

    sub_graph = Graph()

    def walk(head, hops):
        s, p, o = hops[0]
        for instance_ in graph.objects(subject=head, predicate=p):
            sub_graph.add((head, p, instance_))

            hops_ = hops[1:]
            if hops_:
                walk(instance_, hops_)

    for walk_ in walks_:
        walk(instance, walk_)

    return sub_graph


def extract_sub_graphs_from_rdf_graph(graph: Graph, class_: Node) -> Dict[Node, Graph]:
    graphs = {}
    instances_ = graph.subjects(predicate=RDF.type, object=class_)

    for instance in instances_:
        graphs[instance] = extract_sub_graph_from_rdf_graph(graph, instance)

    return graphs
