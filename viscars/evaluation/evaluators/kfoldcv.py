import os

import pandas as pd
from rdflib import Graph
from sklearn.model_selection import KFold


from viscars.dao import DAO, ContentRecommenderDAO
from viscars.evaluation.metrics import MetricType
from viscars.evaluation.metrics.factory import MetricFactory
import viscars.recommenders as recommenders
from viscars.recommenders.base import Recommender


class KFoldCrossValidation:

    def __init__(self, dao: DAO, recommender: Recommender, metrics: [], k=5):
        """
        :param dao: Viscars.DAO: Data Access Object
        :param recommender: Recommender
        :param metrics: List of Metrics
        :param k: Number of folds
        """
        self.dao = dao
        self.recommender = recommender
        self.metrics = metrics
        self.k = k

    def split_k_folds(self):
        dashboards = pd.unique(self.dao.ratings['dashboard'])
        kf = KFold(n_splits=self.k, shuffle=True)

        folds = []
        for train_idx, test_idx, in kf.split(dashboards):
            train_dashboards = dashboards[train_idx]
            test_dashboards = dashboards[test_idx]

            train_ratings = self.dao.ratings[self.dao.ratings['dashboard'].isin(train_dashboards)]
            test_ratings = self.dao.ratings[self.dao.ratings['dashboard'].isin(test_dashboards)]

            folds.append((train_ratings, test_ratings))

        return folds

    def evaluate(self, **kwargs):
        result = {'folds': [], 'result': {}}
        for train, test in self.split_k_folds():
            graph = self.dao.build_subgraph_from_ratings(train)
            self.recommender.set_graph(graph)

            fold_scores = {}

            for uid in test['u_id'].unique():
                df_user = test.loc[test['u_id'] == uid]

                for cid in df_user['c_id'].unique():
                    predictions = self.recommender.predict(uid, cid, **kwargs)
                    recommendations = [r['itemId'] for r in predictions]

                    truth = list(self.dao.ratings.loc[self.dao.ratings['u_id'] == uid]
                                 .loc[self.dao.ratings['c_id'] == cid]['i_id'])

                    for metric in self.metrics:
                        if str(metric) not in fold_scores.keys():
                            fold_scores[str(metric)] = []
                        score = metric.calculate(recommendations[:len(truth)], truth)
                        fold_scores[str(metric)].append(score)

            result_for_fold = {}
            for metric, scores in fold_scores.items():
                avg = sum(scores) / len(scores)
                result_for_fold[metric] = avg

                if metric not in result['result'].keys():
                    result['result'][metric] = []
                result['result'][metric].append(avg)
            result['folds'].append(result_for_fold)

        final_results = {}
        for metric_type, score in result['result'].items():
            final_results[metric_type] = sum(score) / len(score)

        result['result'] = final_results
        return result


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../../dao/protego/protego_ddashboard.ttl')
    graph_.parse('../../dao/protego/protego_zplus.ttl')
    graph_.parse('../../dao/protego/visualizations.ttl')

    dao_ = ContentRecommenderDAO(graph_)

    metric_factory = MetricFactory()

    metrics = ['precision@1', 'recall@1', 'f1@1', 'ndcg@1', 'ndcg@3']
    parsed_metrics = []
    for metric in metrics:
        m_split = metric.split('@')
        m_type = m_split[0]
        n = int(m_split[1]) if len(m_split) >= 2 else None

        metric_ = metric_factory.get(MetricType.reverse_lookup(m_type))
        parsed_metrics.append(metric_)

    recommender = recommenders.RandomRank(dao_)
    evaluator = KFoldCrossValidation(dao_, recommender, metrics=parsed_metrics, k=5)

    result = evaluator.evaluate()
    print(result)
