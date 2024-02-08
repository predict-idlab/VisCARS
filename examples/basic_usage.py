from rdflib import Graph, RDF, SOSA

from viscars.namespace import DASHB
from viscars.recommenders.factory import RecommenderFactory, RecommenderType


if __name__ == '__main__':
    graph = Graph()
    graph.load('../dao/proeftuin/graph.ttl', format='ttl')

    factory = RecommenderFactory()
    recommender = factory.get(RecommenderType.PPR)(graph, alpha=0.8)

    recommender.set_personalization(0.7, 0.3)

    users = graph.subjects(RDF.type, DASHB.User)
    contexts = graph.subjects(RDF.type, SOSA.ObservableProperty)

    uid = users.__next__()
    cid = contexts.__next__()

    print(f'Predictions for uid={uid} and cid={cid}:')
    predictions = recommender.predict(uid, cid)
    print(predictions)
