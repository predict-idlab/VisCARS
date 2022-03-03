from viscars.evaluation.evaluators import Evaluator
from viscars.recommenders import Recommender


class LeaveOneOutCrossValidation(Evaluator):

    def __init__(self, project_id: str, recommender: Recommender, metrics: []):
        """
        :param recommender: Recommender
        :param metrics: List of MetricTypes
        :param k: Number of folds
        """
        super().__init__(project_id, recommender, metrics)

    def _split_ratings(self, uid):
        ratings = self.dLoader.ratings
        train = ratings[ratings['user'] != uid]
        test = ratings[ratings['user'] == uid]

        return train, test

    def evaluate(self, **kwargs):
        users = self.dLoader.user_metadata

        result = {'folds': [], 'result': {}}
        for uid in users['id'].unique():
            train, test = self._split_ratings(uid)

            graph = self.dLoader.build_subgraph_from_ratings(train)
            self.recommender.set_graph(graph)

            fold_scores = {}


            df_user = test.loc[test['user'] == uid]

            for cid in df_user['context']:
                predictions = self.recommender.predict(uid, cid, **kwargs)
                recommendations = [r['itemId'] for r in predictions]

                truth = []
                t_user = test.loc[test['user'] == uid]
                for idx, row in t_user.iterrows():
                    if row['context'] == cid:
                        truth.append(row['item'])
                #truth = list(test.loc[test['user'] == uid].loc[test['context'] == cid]['item'])

                for metric in self.metrics:
                    if str(metric) not in fold_scores.keys():
                        fold_scores[str(metric)] = []
                    score = metric.calculate(recommendations, truth)
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
