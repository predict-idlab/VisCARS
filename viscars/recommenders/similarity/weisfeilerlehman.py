import grakel
from grakel.kernels import WeisfeilerLehman as WeisfeilerLehmanKernel, VertexHistogram
import json
import os
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph

from viscars.dao import DAO


class WeisfeilerLehman:

    def __init__(self, dao: DAO, subjects: [str], cache_file: str = None, verbose: bool = False):
        self.dao = dao
        self.subjects = subjects

        if cache_file is not None:
            self.cache_path = os.path.dirname(cache_file)
            self.cache_file = cache_file

        self._build_model()

    def read_cache(self):
        similarity = {}
        if os.path.exists(self.cache_file):
            with open(self.cache_file) as f_:
                similarity = json.load(f_)
        return similarity

    def write_cache(self, similarity):
        if not os.path.exists(self.cache_path):
            os.makedirs(self.cache_path)

        with open(self.cache_file, 'w') as f_:
            f_.write(json.dumps(similarity))

    def delete_cache(self):
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)

    def _build_model(self):
        rdf_graphs = {}
        for s in self.subjects:
            rdf_graphs[s] = self.dao.build_subgraph_from_subject(s)

        self.grakel_graphs = {}
        for id_, graph in rdf_graphs.items():
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
        similarity_matrix = self.read_cache()

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

        self.write_cache(similarity_matrix)
        return similarity_matrix

    def transform(self):
        pass
