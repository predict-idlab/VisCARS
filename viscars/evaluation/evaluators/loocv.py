from rdflib import Graph

from viscars.dao import DAO, ContentRecommenderDAO
from viscars.evaluation.metrics import MetricType
from viscars.evaluation.metrics.factory import MetricFactory
import viscars.recommenders as recommenders
from viscars.recommenders.base import Recommender


class LeaveOneOutCrossValidation:

    def __init__(self, dao: DAO, recommender: Recommender, metrics: []):
        """
        :param dao: Viscars.DAO: Data Access Object
        :param recommender: Recommender
        :param metrics: List of MetricTypes
        """
        self.dao = dao
        self.recommender = recommender
        self.metrics = metrics

    def _split_ratings(self, uid):
        train = self.dao.ratings[self.dao.ratings['u_id'] != uid]
        test = self.dao.ratings[self.dao.ratings['u_id'] == uid]

        return train, test

    def evaluate(self, **kwargs):
        users = self.dao.ratings['u_id'].unique()

        result = {'folds': [], 'result': {}}
        for uid in users:
            train, test = self._split_ratings(uid)

            graph = self.dao.build_subgraph_from_ratings(train)
            self.recommender.set_graph(graph)

            fold_scores = {}

            df_user = test.loc[test['u_id'] == uid]

            for cid in df_user['c_id']:
                predictions = self.recommender.predict(uid, cid, **kwargs)
                recommendations = [r['itemId'] for r in predictions]

                truth = list(self.dao.ratings.loc[self.dao.ratings['u_id'] == uid]
                             .loc[self.dao.ratings['c_id'] == cid]['i_id'])

                for metric in self.metrics:
                    if str(metric) not in fold_scores.keys():
                        fold_scores[str(metric)] = []
                    score = metric.calculate(recommendations[:len(truth)], truth)
                    fold_scores[str(metric)].append(score)

            result_for_fold = {'uid': uid}
            for metric_type, scores in fold_scores.items():
                avg = sum(scores) / len(scores)
                result_for_fold[metric_type] = avg

                if metric_type not in result['result'].keys():
                    result['result'][metric_type] = []
                result['result'][metric_type].append(avg)
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

    recommender = recommenders.CF(dao_)
    evaluator = LeaveOneOutCrossValidation(dao_, recommender, metrics=parsed_metrics)

    result = evaluator.evaluate()
    print(result)
