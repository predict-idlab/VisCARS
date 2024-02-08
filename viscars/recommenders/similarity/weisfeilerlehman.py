import grakel
from grakel.kernels import WeisfeilerLehman as WeisfeilerLehmanKernel, VertexHistogram
import json
import os
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph

from viscars.dao import DAO


class WeisfeilerLehman:

    CACHE_PATH = os.path.join(os.path.dirname(__file__), '.output/cache')
    CACHE_FILE = os.path.join(CACHE_PATH, 'wf_cache.json')

    def __init__(self, dao: DAO, verbose=False):
        self.dao = dao
        self._build_model()

    @classmethod
    def read_cache(cls):
        similarity = {}
        if os.path.exists(cls.CACHE_FILE):
            with open(cls.CACHE_FILE) as f_:
                similarity = json.load(f_)
        return similarity

    @classmethod
    def write_cache(cls, similarity):
        if not os.path.exists(cls.CACHE_PATH):
            os.makedirs(cls.CACHE_PATH)

        with open(cls.CACHE_FILE, 'w') as f_:
            f_.write(json.dumps(similarity))

    @classmethod
    def delete_cache(cls):
        if os.path.exists(cls.CACHE_FILE):
            os.remove(cls.CACHE_FILE)

    def _build_model(self):
        self.grakel_graphs = {}

        for id_, graph in self.dao.build_subgraphs_from_contexts().items():
            networkx_graph = rdflib_to_networkx_digraph(graph,
                                                        edge_attrs=lambda s, p, o: {'label': p})
            # Add node labels
            for label, data in networkx_graph.nodes(data=True):
                data['label'] = label
            self.grakel_graphs[id_] = \
                list(grakel.utils.graph_from_networkx([networkx_graph],
                                                      node_labels_tag='label',
                                                      edge_labels_tag='label',
                                                      edge_weight_tag='weight'))[0]

    def fit(self):
        pass

    def fit_transform(self):
        similarity_matrix = self.__class__.read_cache()

        for id_, graph in self.grakel_graphs.items():
            if id_ not in similarity_matrix.keys():
                gk = WeisfeilerLehmanKernel(n_iter=2, normalize=True, base_graph_kernel=VertexHistogram)
                check = gk.fit_transform([graph])[0]

                assert (check == 1)

                similarity_matrix[id_] = {}
                for idx_, graph_ in self.grakel_graphs.items():
                    if id_ == idx_:
                        similarity_matrix[id_][idx_] = float(check)
                    if idx_ in similarity_matrix.keys():
                        if id_ in similarity_matrix[idx_].keys():
                            similarity_matrix[id_][idx_] = similarity_matrix[idx_][id_]
                        else:
                            sim_ = float(gk.transform([graph_])[0])
                            similarity_matrix[id_][idx_] = sim_
                            similarity_matrix[idx_][id_] = sim_
                    else:
                        similarity_matrix[id_][idx_] = float(gk.transform([graph_])[0])

        self.__class__.write_cache(similarity_matrix)
        return similarity_matrix

    def transform(self):
        pass
