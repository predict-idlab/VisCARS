import copy
from rdflib import Graph
import time

from viscars.dao import DAO, ContentRecommenderDAO, VisualizationRecommenderDAO
from viscars.recommenders.base import Recommender
from viscars.recommenders.similarity.factory import SimilarityMetricType, SimilarityMetricFactory


class ContextAwareCollaborativeFiltering(Recommender):

    def __init__(self, dao: DAO,
                 similarity_metric: SimilarityMetricType = SimilarityMetricType.WL, cbcf_w: float = 0, ubcf_w: float = 0, verbose=False):
        factory = SimilarityMetricFactory()

        self.cbcf_w = cbcf_w
        self.ubcf_w = ubcf_w

        if self.cbcf_w > 0:
            self.cbcf_similarity_metric = factory.get(similarity_metric)(
                dao, subjects=dao.contexts['id'],
                cache_file='.output/cache/cbcf_similarity.json',
                verbose=verbose
            )

        if self.ubcf_w > 0:
            self.ubcf_similarity_metric = factory.get(similarity_metric)(
                dao, subjects=dao.users['id'],
                cache_file='.output/cache/ubcf_similarity.json',
                verbose=verbose
            )

        super().__init__(dao, verbose)

    def _build_model(self):
        self.logger.info('Building model...')

        if self.cbcf_w:
            self.logger.info('Calculating CBCF similarities...')
            self.cbcf_similarity_matrix = self.cbcf_similarity_metric.fit_transform()
            for k, v in self.cbcf_similarity_matrix.items():
                self.cbcf_similarity_matrix[k] = \
                    {k: v for k, v in sorted(self.cbcf_similarity_matrix[k].items(), key=lambda x: x[1], reverse=True)}

        if self.ubcf_w:
            self.logger.info('Calculating UBCF similarities...')
            self.ubcf_similarity_matrix = self.ubcf_similarity_metric.fit_transform()
            for k, v in self.ubcf_similarity_matrix.items():
                self.ubcf_similarity_matrix[k] = \
                    {k: v for k, v in sorted(self.ubcf_similarity_matrix[k].items(), key=lambda x: x[1], reverse=True)}

        self.logger.info('Model built.')

    def knn_cbcf(self, u_id, c_id, i_id, k, strict=True):
        self.logger.debug('Calculating CBCF KNN for user [{}] and context [{}]'.format(u_id, c_id))
        similarity_matrix_ = copy.deepcopy(self.cbcf_similarity_matrix)

        if c_id in similarity_matrix_[c_id].keys():
            similarity_matrix_[c_id].pop(c_id)

        contexts = self.dao.contexts
        context_type = contexts[contexts['id'] == c_id]['type'].values[0]
        if context_type is not None:
            filtered_contexts = contexts[contexts['type'] == context_type]['id']
        else:
            filtered_contexts = [c_id]

        filtered_neighbors = list(self.dao.ratings[self.dao.ratings['c_id'].isin(filtered_contexts)]['u_id'])
        neighbors = list(self.cbcf_similarity_matrix[c_id].items())
        kn_neighbors = []
        i = 0
        while len(kn_neighbors) < k and i < len(self.cbcf_similarity_matrix):
            c, w = neighbors[i]
            if c in filtered_neighbors:
                kn_neighbors.append((c, w))

            i += 1

        self.logger.debug('KNN calculated: [{}]'.format(len(kn_neighbors)))
        self.logger.debug('KNN: [{}]'.format(kn_neighbors))
        return kn_neighbors

    def knn_ubcf(self, u_id, c_id, i_id, k, strict=True):
        self.logger.debug('Calculating UBCF KNN for user [{}] and context [{}]'.format(u_id, c_id))
        similarity_matrix_ = copy.deepcopy(self.ubcf_similarity_matrix)

        if u_id in similarity_matrix_[u_id].keys():
            similarity_matrix_[u_id].pop(u_id)

        contexts = self.dao.contexts
        context_type = contexts[contexts['id'] == c_id]['type'].values[0]
        if context_type is not None:
            filtered_contexts = contexts[contexts['type'] == context_type]['id']
        else:
            filtered_contexts = [c_id]

        filtered_neighbors = list(self.dao.ratings[self.dao.ratings['c_id'].isin(filtered_contexts)]['u_id'])
        # filtered_neighbors = self.dao.get_ratings_for_context(u_id, c_id, i_id, strict=False)
        neighbors = list(self.ubcf_similarity_matrix[u_id].items())
        kn_neighbors = []
        i = 0
        while len(kn_neighbors) < k and i < len(self.ubcf_similarity_matrix):
            u, w = neighbors[i]
            if u in filtered_neighbors:
                kn_neighbors.append((u, w))

            i += 1

        self.logger.debug('KNN calculated: [{}]'.format(len(kn_neighbors)))
        self.logger.debug('KNN: [{}]'.format(kn_neighbors))
        return kn_neighbors

    def predict_cbcf(self, u_id, c_id, i_id, k, strict=True):
        # Calculate K-nearest neighbours
        neighbours = self.knn_cbcf(u_id, c_id, i_id, k, strict)

        total_rw = 0
        total_w = 0

        users = self.dao.users
        user_type = users[users['id'] == u_id]['type'].values[0]
        if user_type is not None:
            filtered_users = users[users['type'] == user_type]['id']
        else:
            filtered_users = [u_id]

        items = self.dao.items
        item_type = items[items['id'] == i_id]['type'].values[0]
        if item_type is not None:
            filtered_items = items[items['type'] == item_type]['id']
        else:
            filtered_items = [i_id]

        for n, w in neighbours:
            r_aui = not self.dao.ratings[
                (self.dao.ratings['u_id'].isin(filtered_users))
                & (self.dao.ratings['i_id'].isin(filtered_items))
                & (self.dao.ratings['c_id'] == n)
            ].empty
            # r_aui = not self.dao.get_context_neighborhood_ratings(u_id=u_id, c_id=n, i_id=i_id).empty
            w_au = w  # Similarity score
            total_rw += r_aui * w_au
            total_w += w
            self.logger.debug('r_aui: [{}] w_au: [{}] total_rw: [{}] total_w: [{}]'.format(r_aui, w_au, total_rw, total_w))
        return total_rw / total_w if total_w > 0 else 0

    def predict_ubcf(self, u_id, c_id, i_id, k, strict=True):
        # Calculate K-nearest neighbours
        neighbours = self.knn_ubcf(u_id, c_id, i_id, k, strict)

        total_rw = 0
        total_w = 0

        items = self.dao.items
        item_type = items[items['id'] == i_id]['type'].values[0]
        if item_type is not None:
            filtered_items = items[items['type'] == item_type]['id']
        else:
            filtered_items = [i_id]

        contexts = self.dao.contexts
        context_type = contexts[contexts['id'] == c_id]['type'].values[0]
        if context_type is not None:
            filtered_contexts = contexts[contexts['type'] == context_type]['id']
        else:
            filtered_contexts = [c_id]

        for n, w in neighbours:
            r_aui = not self.dao.ratings[
                (self.dao.ratings['u_id'] == n)
                & (self.dao.ratings['i_id'].isin(filtered_items))
                & (self.dao.ratings['c_id'].isin(filtered_contexts))
            ].empty
            # r_aui = not self.dao.get_neighbor_ratings(u_id=u_id, c_id=n, i_id=i_id).empty
            w_au = w  # Similarity score
            total_rw += r_aui * w_au
            total_w += w
            self.logger.debug('r_aui: [{}] w_au: [{}] total_rw: [{}] total_w: [{}]'.format(r_aui, w_au, total_rw, total_w))
        return total_rw / total_w if total_w > 0 else 0

    def predict(self, u_id, c_id, k: int = 20, *kwargs):
        scores = {}
        for i_id in self.dao.get_items_by_context(c_id):
            cbcf_score = self.predict_cbcf(u_id, c_id, i_id, k) if self.cbcf_w > 0 else 0
            ubcf_score = self.predict_ubcf(u_id, c_id, i_id, k) if self.ubcf_w > 0 else 0
            scores[i_id] = self.cbcf_w * cbcf_score + self.ubcf_w * ubcf_score

        recommendations = [{'contextId': c_id, 'itemId': item, 'score': score} for item, score in scores.items()]
        results = sorted(recommendations, key=lambda n: n['score'], reverse=True)
        return results

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass
