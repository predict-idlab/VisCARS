import argparse
import json
import os
from random import randint
from rdflib import Graph, URIRef, BNode
from rdflib.namespace import RDF, SOSA
import sys
from time import sleep, time
from tqdm import tqdm

from viscars.dao import DAO, VisualizationRecommenderDAO, ContentRecommenderDAO
import viscars.evaluation.evaluators as evaluators
from viscars.evaluation.metrics import MetricType
from viscars.evaluation.metrics.factory import MetricFactory
from viscars.namespace import DASHB
import viscars.recommenders as recommenders
from viscars.recommenders import PPR

sys.path.insert(0, os.path.dirname(os.getcwd()))


class PerformanceEvaluator:

    def __init__(self, dao: DAO):
        self.dao = dao

    def run(self, evaluator, recommenders, metrics, iter=5, sleep_=10, output_path_=None):
        metric_factory = MetricFactory()

        parsed_metrics = []
        for metric in metrics:
            m_split = metric.split('@')
            m_type = m_split[0]
            n = int(m_split[1]) if len(m_split) >= 2 else None

            metric_ = metric_factory.get(MetricType.reverse_lookup(m_type), n)
            parsed_metrics.append(metric_)

        results = {}
        for id_, cls in tqdm(recommenders.items()):
            recommender_ = cls(self.dao)
            evaluator_ = evaluator(self.dao, recommender_, metrics=parsed_metrics)

            scores = {}
            for _ in range(iter):
                sleep(sleep_)

                scores_ = evaluator_.evaluate()
                for metric_, score_ in scores_['result'].items():
                    if metric_ in scores.keys():
                        scores[metric_] += score_
                    else:
                        scores[metric_] = score_

            scores = {k: v / iter for k, v in scores.items()}
            results[id_] = scores
            if output_path_ is not None:
                with open(os.path.join(output_path_, 'performance.json'), 'w') as output_f:
                    output_f.write(json.dumps(results))

        return results


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../data/protego-2/protego_ddashboard.ttl')
    graph_.parse('../data/protego-2/protego_zplus.ttl')
    graph_.parse('../data/protego-2/visualizations.ttl')

    dao_ = VisualizationRecommenderDAO(graph_)

    recommender_ = PPR(dao_)
    evaluator_ = evaluator(self.dao, recommender_, metrics=parsed_metrics)

    evaluator = PerformanceEvaluator(dao_)
    metrics = ['f1@1']
    vis_results_kfold = evaluator.run(evaluators.KFoldCrossValidation, models_, metrics, iter=iter_, sleep_=sleep_, output_path_=output_path)
    vis_results_loocv = evaluator.run(evaluators.LeaveOneOutCrossValidation, models_, metrics, iter=iter_, sleep_=sleep_, output_path_=output_path)

    dao_ = ContentRecommenderDAO(graph_)
    evaluator = PerformanceEvaluator(dao_)
    metrics = ['f1', 'ndcg']
    content_results_kfold = evaluator.run(evaluators.KFoldCrossValidation, models_, metrics, iter=iter_, sleep_=sleep_, output_path_=output_path)
    content_results_loocv = evaluator.run(evaluators.LeaveOneOutCrossValidation, models_, metrics, iter=iter_, sleep_=sleep_, output_path_=output_path)

    results = {
        'visualization_rec': {
            'kfold': vis_results_kfold,
            'loocv': vis_results_loocv
        },
        'content_rec': {
            'kfold': content_results_kfold,
            'loocv': content_results_loocv
        }
    }

    with open(os.path.join(output_path, 'performance.json'), 'w') as output_f:
        output_f.write(json.dumps(results))
