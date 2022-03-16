import pandas as pd
from rdflib import Graph

from viscars.namespace import DASHB
from viscars.utils import clean_graph


class DataLoader:

    def __init__(self, graph: Graph):
        self.graph = graph
        clean_graph(graph)

        self.ratings = self.extract_ratings_from_graph()
        self.user_metadata = self.extract_users_from_graph()
        self.context_metadata = self.extract_contexts_from_graph()
        self.item_metadata = self.extract_items_from_graph()

    # def load_graph(self) -> Graph:
    #     graph = Graph()
    #     graph.parse(f'./data/{self.project}/graph.ttl', format='n3')
    #
    #     return clean_graph(graph)

    def build_subgraph_from_ratings(self, ratings: pd.DataFrame) -> Graph:
        sub_graph = Graph()

        for idx, row in self.context_metadata.iterrows():
            cid = row['id']
            sub_graph += self.graph.triples((cid, None, None))

        for idx, row in self.user_metadata.iterrows():
            uid = row['id']
            sub_graph += self.graph.triples((uid, DASHB.memberOf, None))

        for idx, row in self.item_metadata.iterrows():
            iid = row['id']
            sub_graph += self.graph.triples((iid, None, None))

        for idx, row in ratings.iterrows():
            uid = row['user']
            iid = row['item']
            cid = row['context']

            sub_graph += self.graph.triples((uid, None, None))
            sub_graph += self.graph.triples((None, None, uid))
            sub_graph += self.graph.triples((iid, None, None))
            sub_graph += self.graph.triples((None, None, iid))

            for cid_ in cid:
                sub_graph += self.graph.triples((cid_, None, None))
                sub_graph += self.graph.triples((None, None, cid_))

        return sub_graph

    def extract_ratings_from_graph(self) -> pd.DataFrame:
        qry = '''
            prefix dashb: <https://docs.dynamicdashboard.ilabt.imec.be/ontologies/dashboard#>

            SELECT ?widget ?user ?visualization WHERE {
                ?widget dashb:visualizedBy ?visualization ;
                        dashb:createdBy ?user .
            }
        '''
        result = self.graph.query(qry)

        ratings = pd.DataFrame(columns=['user', 'item', 'rating', 'context'])
        for row in result:
            widget_ = row[0]
            user_ = row[1]

            qry = f'''
                prefix dashb: <https://docs.dynamicdashboard.ilabt.imec.be/ontologies/dashboard#>

                SELECT ?property WHERE {{
                    <{widget_}> dashb:hasProperty ?property .
                }}
            '''
            properties = [str(row[0]) for row in self.graph.query(qry)]

            ratings = ratings.append({'user': user_, 'item': row[2], 'rating': 5.0, 'context': properties},
                                     ignore_index=True)

        return ratings

    def extract_users_from_graph(self) -> pd.DataFrame:
        qry = '''
            prefix dashb: <https://docs.dynamicdashboard.ilabt.imec.be/ontologies/dashboard#>

            SELECT ?user ?username ?role WHERE {
                ?user dashb:memberOf ?role .
            }
        '''
        user_metadata = pd.DataFrame(columns=['id', 'type'])

        result = self.graph.query(qry)
        for row in result:
            user_metadata = user_metadata.append({'id': row[0], 'type': row[2]}, ignore_index=True)

        return user_metadata

    def extract_contexts_from_graph(self) -> pd.DataFrame:
        qry = '''
            prefix dashb: <http://docs.dynamicdashboard.ilabt.imec.be/ontologies/dashboard#>

            SELECT ?property ?metric WHERE {
                ?property dashb:produces ?metric .
            }
        '''
        context_metadata = pd.DataFrame(columns=['id', 'type'])

        result = self.graph.query(qry)
        for row in result:
            context_metadata = context_metadata.append({'id': row[0], 'type': row[1]}, ignore_index=True)

        return context_metadata

    def extract_items_from_graph(self) -> pd.DataFrame:
        qry = '''
            prefix dashb: <http://docs.dynamicdashboard.ilabt.imec.be/ontologies/dashboard#>

            SELECT ?visualization WHERE {
                ?visualization a dashb:Visualization .
            }
        '''
        item_metadata = pd.DataFrame(columns=['id'])

        result = self.graph.query(qry)
        for row in result:
            item_metadata = item_metadata.append({'id': row[0]}, ignore_index=True)

        return item_metadata

    def get_graph(self) -> Graph:
        return self.graph

    def set_graph(self, graph: Graph):
        self.graph = graph

        self.ratings = self.extract_ratings_from_graph()
        self.user_metadata = self.extract_users_from_graph()
        self.context_metadata = self.extract_contexts_from_graph()
