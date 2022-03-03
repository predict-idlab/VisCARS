from sklearn.model_selection import KFold

from viscars.evaluation.evaluators import Evaluator
from viscars.recommenders import Recommender


class KFoldCrossValidation(Evaluator):

    def __init__(self, project_id: str, recommender: Recommender, metrics: [], k=5):
        """
        :param project_id: ID of the project (to load the correct data).
        :param recommender: Recommender
        :param metrics: List of Metrics
        :param k: Number of folds
        """
        super().__init__(project_id, recommender, metrics)

        self.k = k

    def evaluate(self, **kwargs):
        ratings = self.dLoader.ratings
        kf = KFold(n_splits=self.k, shuffle=True)

        n_fold = 0

        result = {'folds': [], 'result': {}}
        for train_idx, test_idx in kf.split(ratings):
            train = ratings.iloc[train_idx]
            test = ratings.iloc[test_idx]

            graph = self.dLoader.build_subgraph_from_ratings(train)
            self.recommender.set_graph(graph)

            fold_scores = {}

            for uid in test['user'].unique():
                df_user = test.loc[test['user'] == uid]

                for cid in df_user['context']:
                    predictions = self.recommender.predict(uid, cid, **kwargs)
                    recommendations = [r['itemId'] for r in predictions]

                    truth = []
                    t_user = test.loc[test['user'] == uid]
                    for idx, row in t_user.iterrows():
                        if row['context'] == cid:
                            truth.append(row['item'])
                    # truth = list(test.loc[test['user'] == uid].loc[test['context'] == cid]['item'])

                    for metric in self.metrics:
                        if str(metric) not in fold_scores.keys():
                            fold_scores[str(metric)] = []
                        score = metric.calculate(recommendations, truth)
                        fold_scores[str(metric)].append(score)

            result_for_fold = {}
            for metric, scores in fold_scores.items():
                avg = sum(scores) / len(scores)
                result_for_fold[metric] = avg

                if metric not in result['result'].keys():
                    result['result'][metric] = []
                result['result'][metric].append(avg)
            result['folds'].append(result_for_fold)

            n_fold += 1

        final_results = {}
        for metric_type, score in result['result'].items():
            final_results[metric_type] = sum(score) / len(score)

        result['result'] = final_results
        return result
