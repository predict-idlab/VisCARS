import numpy as np
import os
import pandas as pd
from pyrdf2vec import RDF2VecTransformer
from pyrdf2vec.embedders import Word2Vec
from pyrdf2vec.graphs import KG
from pyrdf2vec.walkers import RandomWalker
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, SOSA, SSN
from tqdm import tqdm

from viscars.namespace import DASHB

# TODO: Move to configuration
from viscars.recommenders.similarity import SimilarityMetric

CONTEXT_CLASS = SSN.System
USER_CLASS = DASHB.User
# ITEM_CLASS = DASHB.Visualization
ITEM_CLASS = SOSA.ObservableProperty


class RDF2VecEmbedding(SimilarityMetric):

    def __init__(self, graph: Graph, verbose=False):
        super().__init__(graph, verbose)

        self.kg = KG(
            os.path.join('D:\\Documents\\UGent\\PhD\\projects\\PhD\\VisCARS\\data\\protego', 'graph.ttl')
        )

        self.verbose = verbose

        self._build_model()

    def _build_model(self):
        self.transformer = RDF2VecTransformer(
            Word2Vec(epochs=10),
            walkers=[RandomWalker(4, 10, with_reverse=False, n_jobs=2)],
            # verbose=1
        )

        self.entities = pd.DataFrame()

        entity_types = {}
        for result in self.graph.subject_objects(predicate=RDF.type):
            entity = str(result[0])
            type_ = str(result[1])

            if entity not in entity_types.keys():
                entity_types[entity] = [type_]
            else:
                entity_types[entity].append(type_)

        self.entities.loc[:, ('id')] = [e.name for e in self.kg._entities]
        self.entities.loc[:, ('type')] = [', '.join(entity_types[row['id']]) if row['id'] in entity_types.keys() else 'None'
                                     for idx, row in self.entities.iterrows()]

    def fit(self):
        pass

    def fit_transform(self, entity_class: str):
        contexts = set(self.graph.subjects(RDF.type, USER_CLASS))

        embeddings, literals = self.transformer.fit_transform(self.kg, [e.name for e in self.kg._entities])
        embeddings = np.array(embeddings)

        similarity = {}

        for idx, cid in tqdm(enumerate(contexts), total=len(contexts)):
            similarity[cid] = {}

            embedding = embeddings[idx]

            for idx_, cid_ in enumerate(contexts):
                embedding_ = embeddings[idx_]

                if cid == cid_:
                    similarity[cid][cid_] = 1
                elif cid_ in similarity.keys():
                    similarity[cid][cid_] = similarity[cid_][cid]
                else:
                    similarity[cid][cid_] = 1 - float(np.linalg.norm(embedding - embedding_))

        return similarity

    def transform(self):
        pass


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse(os.path.join('D:\\Documents\\UGent\\PhD\\projects\\PhD\\VisCARS\\data\\protego', 'graph.ttl'))
    rdf2vec = RDF2VecEmbedding(graph_)
    distances_ = rdf2vec.fit_transform(CONTEXT_CLASS)
    print(distances_)
