# VisCARS: Graph-Based Context-Aware Visualization Recommendation System

![version](https://img.shields.io/pypi/v/viscars)

## Installation

Create a virtual environment using `virtualenv` or `anaconda3`:
```
conda create -n myenv python=3.9
conda activate myenv
```

Install the latest version from PyPI in your environment:
```
pip install viscars
```

## Basic usage

Load the dataset
```python
from rdflib import Graph

graph_ = Graph()
graph_.parse('../data/protego/protego_ddashboard.ttl')
graph_.parse('../data/protego/protego_zplus.ttl')
graph_.parse('../data/protego/visualizations.ttl')
```

Initialize the two-stage recommendation pipeline
```python
from viscars.dao import ContentRecommenderDAO, VisualizationRecommenderDAO
from viscars.recommenders.cacf import ContextAwareCollaborativeFiltering

# Initialize Content Recommender (stage 1)
content_dao = ContentRecommenderDAO(graph_)
content_recommender = ContextAwareCollaborativeFiltering(content_dao, cbcf_w=0.5, ubcf_w=0.5, verbose=False)

# Initialize Visualization Recommender (stage 2)
vis_dao = VisualizationRecommenderDAO(graph_)
visualization_recommender = ContextAwareCollaborativeFiltering(vis_dao, ubcf_w=1, verbose=False)
```

Run the pipeline for a user and context
```python
# user = 'https://dynamicdashboard.ilabt.imec.be/users/4'  # Operator
user = 'https://dynamicdashboard.ilabt.imec.be/users/5'  # Nurse

context = 'http://example.com/tx/patients/zplus_6'  # Diabetes

content_recommendations = content_recommender.predict(user, context, k=5)

# Find cutoff for Multiple-View recommendation
# We recommend the top x items, where x is the average number of items rated by users in the context
ratings = content_dao.ratings[(content_dao.ratings['c_id'] == context)]
c = int(ratings.value_counts('u_id').mean())

visualization_recommendations = []
for recommendation in content_recommendations[:c]:
    # Recommend visualizations
    recommendations = visualization_recommender.predict(user, recommendation['itemId'], k=5)
    visualization_recommendations.append(recommendations[0])
```

Example output

| propertyId                                                                                                            | visualizationId                                                                  | score |
|-----------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------| --- |
| https://.../things/zplus_6.lifestyle/properties/enriched-call                                                         | http://.../things/visualizations/enriched-call                                   | 1.0 |
| https://.../things/zplus_6.60%3A77%3A71%3A7D%3A93%3AD7%2Fservice0009/properties/org.dyamand.types.health.GlucoseLevel | http://.../things/visualizations/time-series-line-chart-with-time-range-selector | 0.6923076923076923 |
| https://.../things/zplus_6.AQURA_10_10_145_9/properties/org.dyamand.aqura.AquraLocationState_Protego%20User           | http://.../things/visualizations/scrolling-table                                 | 1.0 |




## Citation
