from rdflib import Graph

from viscars.dao import ContentRecommenderDAO, VisualizationRecommenderDAO
from viscars.recommenders.cacf import ContextAwareCollaborativeFiltering


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('../data/protego/protego_ddashboard.ttl')
    graph_.parse('../data/protego/protego_zplus.ttl')
    graph_.parse('../data/protego/visualizations.ttl')

    # Initialize Content Recommender (stage 1)
    content_dao = ContentRecommenderDAO(graph_)
    content_recommender = ContextAwareCollaborativeFiltering(content_dao, cbcf_w=0.5, ubcf_w=0.5, verbose=False)

    # Initialize Visualization Recommender (stage 2)
    vis_dao = VisualizationRecommenderDAO(graph_)
    visualization_recommender = ContextAwareCollaborativeFiltering(vis_dao, ubcf_w=1, verbose=False)

    # Recommend content
    # user = 'https://dynamicdashboard.ilabt.imec.be/users/4'  # Operator
    user = 'https://dynamicdashboard.ilabt.imec.be/users/5'  # Nurse
    # user = 'http://example.com/tx/users/6eecba20-ace9-47fb-8ca6-df17b226f6dd'  # Operator
    # user = 'http://example.com/tx/users/157b0cbd-3e61-4892-b4e6-f5803f379d5b'  # Operator

    # context = 'http://example.com/tx/patients/zplus_6'  # Diabetes
    context = 'http://example.com/tx/patients/zplus_235'  # HeartDisease

    content_recommendations = content_recommender.predict(user, context, k=5)

    # Find cutoff for Multiple-View recommendation
    # We recommend the top x items, where x is the average number of items rated by users in the context
    ratings = content_dao.ratings[(content_dao.ratings['c_id'] == context)]
    c = int(ratings.value_counts('u_id').mean())
    print(c)

    print(content_recommendations[:c])

    visualization_recommendations = []
    for recommendation in content_recommendations[:c]:
        # Recommend visualizations
        recommendations = visualization_recommender.predict(user, recommendation['itemId'], k=5)
        print(recommendations)
        visualization_recommendations.append(recommendations[0])

    print(visualization_recommendations)
