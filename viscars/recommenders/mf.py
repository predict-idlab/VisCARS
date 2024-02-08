from funk_svd import SVD
import pandas as pd
import random
from rdflib import Graph

from viscars.dao import DAO, ContentRecommenderDAO
from viscars.recommenders.base import Recommender


class MatrixFactorization(Recommender):
    def __init__(self, dao: DAO, verbose=False):
        super().__init__(dao, verbose)

    def _build_model(self):
        self.ratings = pd.DataFrame({'u_id': [], 'i_id': [], 'rating': [], 'c_id': []})

        # For unique dashboard/c_id pair in dataframe
        for row, size in self.dao.ratings.groupby(['dashboard', 'u_id', 'c_id']).size().items():
            dashboard, user, context = row

            ratings_for_dashboard = self.dao.ratings.loc[self.dao.ratings['dashboard'] == dashboard]
            rated_items_for_dashboard = \
                list(ratings_for_dashboard.loc[ratings_for_dashboard['c_id'] == context]['i_id'])
            for item_ in self.dao.items['id']:
                rating = 1 if item_ in rated_items_for_dashboard else 0
                rating_ = {
                    'u_id': [list(self.dao.users['id']).index(user)],
                    'i_id': [list(self.dao.items['id']).index(item_)],
                    'rating': [rating],
                    'c_id': [list(self.dao.contexts['id']).index(context)]
                }
                self.ratings = pd.concat([self.ratings, pd.DataFrame(rating_)], ignore_index=True)

        convert_dict = {
            'u_id': int,
            'i_id': int,
            'rating': int,
            'c_id': int
        }
        self.ratings = self.ratings.astype(convert_dict)
        self.ratings = self.ratings.drop_duplicates()

        model = SVD(lr=0.001, reg=0.005, n_epochs=100, n_factors=15,
                    early_stopping=True, shuffle=False, min_rating=0, max_rating=1)

        self.model = model
        self.fit()

    def fit(self, ratings: pd.DataFrame = None):
        if ratings is None:
            ratings = self.ratings

        train = ratings.sample(frac=0.8, random_state=7)
        val = ratings.drop(train.index.tolist())

        self.model.fit(X=train, X_val=val)

    def predict(self, u_id, c_id, **kwargs):
        scores = {}
        for i_id in self.dao.items['id']:
            iid = list(self.dao.items['id']).index(i_id)

            if u_id in self.dao.users['id']:
                uid = list(self.dao.users['id']).index(u_id)
            else:
                uid = len(self.dao.users['id']) + 1

            df_ = pd.DataFrame({'u_id': [uid], 'i_id': [iid]})
            scores[i_id] = self.model.predict(df_)[0]

        recommendations = [{'contextId': c_id, 'itemId': item, 'score': score} for item, score in
                           scores.items()]
        random.seed()
        random.shuffle(recommendations)
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../../dao/protego/protego_ddashboard.ttl')
    graph_.parse('../../dao/protego/protego_zplus.ttl')
    graph_.parse('../../dao/protego/visualizations.ttl')

    dao_ = ContentRecommenderDAO(graph_)

    recommender = MatrixFactorization(dao_)
    recommendations = recommender.predict('http://example.com/tx/users/0d619749-5616-43a3-8c93-d81e1d51919e',
                                          'http://example.com/tx/patients/zplus_6')
    print(recommendations)
