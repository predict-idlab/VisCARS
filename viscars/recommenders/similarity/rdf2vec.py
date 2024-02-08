import numpy as np
import pandas as pd
from pyrdf2vec import RDF2VecTransformer
from pyrdf2vec.embedders import Word2Vec
from pyrdf2vec.graphs import KG
from pyrdf2vec.walkers import RandomWalker
import tempfile

from viscars.dao import DAO


class RDF2VecEmbedding:

    def __init__(self, dao: DAO, verbose=False):
        self.dao = dao
        self.verbose = verbose

        self._build_model()

    def _build_model(self):
        self.transformer = RDF2VecTransformer(
            Word2Vec(epochs=10),
            walkers=[RandomWalker(4, 10, with_reverse=False, n_jobs=2)],
            # verbose=1
        )

        self.entities = pd.DataFrame()

        file = tempfile.NamedTemporaryFile()
        self.dao.graph.serialize(file.name)
        self.kg = KG(
            file.name
        )

    def fit(self):
        pass

    def fit_transform(self):
        embeddings, literals = self.transformer.fit_transform(self.kg, [e.name for e in self.kg._entities])
        embeddings = np.array(embeddings)

        similarity_matrix = {}

        for idx, c_id in enumerate(self.dao.contexts):
            similarity_matrix[c_id] = {}

            embedding = embeddings[idx]

            for idx_, c_id_ in enumerate(self.dao.contexts):
                embedding_ = embeddings[idx_]

                if c_id == c_id_:
                    similarity_matrix[c_id][c_id_] = 1
                elif c_id_ in similarity_matrix.keys():
                    similarity_matrix[c_id][c_id_] = similarity_matrix[c_id_][c_id]
                else:
                    similarity_matrix[c_id][c_id_] = 1 - float(np.linalg.norm(embedding - embedding_))

        return similarity_matrix

    def transform(self):
        pass
