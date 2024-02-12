from rdflib import Graph

from viscars.dao import ContentRecommenderDAO, VisualizationRecommenderDAO
from viscars.recommenders.cacf import ContextAwareCollaborativeFiltering


class RecommendationPipeline:

    def __init__(self, graph):
        self.content_dao = ContentRecommenderDAO(graph)
        self.content_recommender = ContextAwareCollaborativeFiltering(self.content_dao, cbcf_w=0.5, ubcf_w=0.5, verbose=False)
        self.vis_dao = VisualizationRecommenderDAO(graph)
        self.visualization_recommender = ContextAwareCollaborativeFiltering(self.vis_dao, ubcf_w=1, verbose=False)

    def recommend_dashboard(self, u_id, c_id):
        content_recommendations = self.content_recommender.predict(u_id, c_id, k=5)

        # Find cutoff for Multiple-View recommendation
        # We recommend the top x items, where x is the average number of items rated by users in the context
        ratings = self.content_dao.ratings[(self.content_dao.ratings['c_id'] == c_id)]
        c = int(ratings.value_counts('u_id').mean())

        dashboard = []
        for r in content_recommendations[:c]:
            visualization_recommendations = self.visualization_recommender.predict(u_id, r['itemId'], k=5)
            recommendation = visualization_recommendations[0]
            dashboard.append({'propertyId': recommendation['contextId'], 'visualizationId': recommendation['itemId']})
        return dashboard


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../data/protego/protego_ddashboard.ttl')
    graph_.parse('../data/protego/protego_zplus.ttl')
    graph_.parse('../data/protego/visualizations.ttl')

    pipeline = RecommendationPipeline(graph_)
    dashboard = pipeline.recommend_dashboard('https://dynamicdashboard.ilabt.imec.be/users/4', 'http://example.com/tx/patients/zplus_6')
    print(dashboard)
