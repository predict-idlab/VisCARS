import logging
from typing import Dict

import pandas as pd
from rdflib import Graph
from rdflib.namespace import RDF, SOSA, SSN

from viscars.namespace import DASHB
from viscars.utils import extract_sub_graph_from_rdf_graph, extract_sub_graphs_from_rdf_graph


class DAO:

    def __init__(self, graph: Graph,
                 user_metaclass=DASHB.User,
                 item_metaclass=DASHB.Visualization,
                 context_metaclass=SOSA.ObservableProperty):
        self.graph = graph

        self.logger = logging.getLogger(__name__)

        self.user_metaclass = user_metaclass
        self.item_metaclass = item_metaclass
        self.context_metaclass = context_metaclass

        self.metadata_graph = self.extract_metadata_graph_from_graph()
        self.contexts = self.extract_contexts_from_graph()
        self.items = self.extract_items_from_graph()
        self.users = self.extract_users_from_graph()
        self.ratings = self.extract_ratings_from_graph()

    def get_items_by_context(self, c_id: str) -> list:
        raise NotImplementedError

    def extract_contexts_from_graph(self) -> pd.DataFrame:
        raise NotImplementedError

    def extract_items_from_graph(self) -> pd.DataFrame:
        raise NotImplementedError

    def extract_users_from_graph(self) -> pd.DataFrame:
        raise NotImplementedError

    def extract_ratings_from_graph(self) -> pd.DataFrame:
        raise NotImplementedError

    def extract_metadata_graph_from_graph(self) -> Graph:
        metadata_graph = Graph()

        # Users
        for _, graph_ in extract_sub_graphs_from_rdf_graph(self.graph, self.user_metaclass).items():
            metadata_graph += graph_.triples((None, None, None))

        # Items
        for _, graph_ in extract_sub_graphs_from_rdf_graph(self.graph, self.item_metaclass).items():
            metadata_graph += graph_.triples((None, None, None))

        # Contexts
        for _, graph_ in extract_sub_graphs_from_rdf_graph(self.graph, self.context_metaclass).items():
            metadata_graph += graph_.triples((None, None, None))

        return metadata_graph

    def build_subgraph_from_ratings(self, ratings: pd.DataFrame) -> Graph:
        subgraph = Graph()
        subgraph += self.metadata_graph.triples((None, None, None))

        for _, row in ratings.iterrows():
            subgraph += extract_sub_graph_from_rdf_graph(self.graph, row.dashboard).triples((None, None, None))
        return subgraph

    def build_subgraphs_from_contexts(self) -> Dict[str, Graph]:
        sub_graphs = {}

        for c_id in self.graph.subjects(RDF.type, self.context_metaclass):
            sub_graph = extract_sub_graph_from_rdf_graph(self.graph, c_id)
            sub_graphs[str(c_id)] = sub_graph

        return sub_graphs

    def get_graph(self) -> Graph:
        return self.graph

    def set_graph(self, graph: Graph):
        self.graph = graph

        self.metadata_graph = self.extract_metadata_graph_from_graph()
        self.contexts = self.extract_contexts_from_graph()
        self.items = self.extract_items_from_graph()
        self.users = self.extract_users_from_graph()
        self.ratings = self.extract_ratings_from_graph()


class ContentRecommenderDAO(DAO):

    USER_METACLASS = DASHB.User
    ITEM_METACLASS = SOSA.ObservableProperty
    CONTEXT_METACLASS = SSN.System

    def __init__(self, graph: Graph):
        super().__init__(
            graph,
            ContentRecommenderDAO.USER_METACLASS,
            ContentRecommenderDAO.ITEM_METACLASS,
            ContentRecommenderDAO.CONTEXT_METACLASS
        )

    def get_items_by_context(self, c_id: str) -> list:
        return list(self.items[self.items['c_id'] == c_id]['id'])

    def extract_contexts_from_graph(self) -> pd.DataFrame:
        ids = [str(context) for context in self.graph.subjects(RDF.type, self.context_metaclass)]
        return pd.DataFrame({
            'id': ids,
            'type': len(ids) * [None]
        })

    def extract_items_from_graph(self) -> pd.DataFrame:
        qry = f'''
            PREFIX ssn-ext: <http://dynamicdashboard.ilabt.imec.be/broker/ontologies/ssn-extension/>
            
            SELECT ?system ?property ?type WHERE {{
                ?sensor ssn-ext:subSystemOf ?system ; 
                    <{SOSA.observes}> ?property .
                    
                OPTIONAL{{ ?property <{DASHB.produces}> ?type . }}
            }}
        '''
        df = pd.DataFrame({'id': [], 'type': [], 'c_id': []})

        for row in self.graph.query(qry):
            df = pd.concat([df, pd.DataFrame({
                'id': [str(row.property)],
                'type': [str(row.type)],
                'c_id': [str(row.system)]
            })])

        return df

    def extract_users_from_graph(self) -> pd.DataFrame:
        qry = f'''
            SELECT ?user ?type WHERE {{
                ?user <{DASHB.memberOf}> ?type .
            }}
        '''
        result = list(self.graph.query(qry))
        return pd.DataFrame({
            'id': [str(row.user) for row in result],
            'type': [str(row.type) for row in result],
        })

    def extract_ratings_from_graph(self) -> pd.DataFrame:
        qry = f'''
            PREFIX ssn-ext: <http://dynamicdashboard.ilabt.imec.be/broker/ontologies/ssn-extension/>

            SELECT ?dashboard ?user ?item ?context WHERE {{
                ?dashboard <{DASHB.hasTab}> ?tab .
                ?tab <{DASHB.hasWidget}> ?widget .

                ?widget <{DASHB.hasProperty}> ?item ;
                    <{DASHB.createdBy}> ?user .

                ?sensor ssn-ext:subSystemOf ?context ;
                    <{SOSA.observes}> ?item .
            }}
        '''
        result = list(self.graph.query(qry))
        return pd.DataFrame({
            'dashboard': [str(row.dashboard) for row in result],
            'u_id': [str(row.user) for row in result],
            'i_id': [str(row.item) for row in result],
            'c_id': [str(row.context) for row in result]
        })


class VisualizationRecommenderDAO(DAO):
    USER_METACLASS = DASHB.User
    ITEM_METACLASS = DASHB.Visualization
    CONTEXT_METACLASS = SOSA.ObservableProperty

    def __init__(self, graph: Graph):
        super().__init__(
            graph,
            VisualizationRecommenderDAO.USER_METACLASS,
            VisualizationRecommenderDAO.ITEM_METACLASS,
            VisualizationRecommenderDAO.CONTEXT_METACLASS
        )

    def get_items_by_context(self, c_id: str) -> list:
        return self.items['id']

    def extract_contexts_from_graph(self) -> pd.DataFrame:
        qry = f'''
            SELECT ?property ?type WHERE {{
                ?sensor <{SOSA.observes}> ?property .
                
                OPTIONAL{{ ?property <{DASHB.produces}> ?type . }}
            }}
        '''
        result = list(self.graph.query(qry))
        return pd.DataFrame({
            'id': [str(row.property) for row in result],
            'type': [str(row.type) for row in result]
        })

    def extract_items_from_graph(self) -> pd.DataFrame:
        ids = [str(item) for item in self.graph.subjects(RDF.type, self.item_metaclass)]
        return pd.DataFrame({
            'id': ids,
            'type': len(ids) * [None],
            'c_id': len(ids) * [None]
        })

    def extract_users_from_graph(self) -> pd.DataFrame:
        qry = f'''
            SELECT ?user ?type WHERE {{
                ?user <{DASHB.memberOf}> ?type .
            }}
        '''
        result = list(self.graph.query(qry))
        return pd.DataFrame({
            'id': [str(row.user) for row in result],
            'type': [str(row.type) for row in result],
        })

    def extract_ratings_from_graph(self) -> pd.DataFrame:
        qry = f'''
            SELECT ?dashboard ?user ?item ?context WHERE {{
                ?dashboard <{DASHB.hasTab}> ?tab .
                ?tab <{DASHB.hasWidget}> ?widget .

                ?widget <{DASHB.hasProperty}> ?context ;
                    <{DASHB.visualizedBy}> ?item ;
                    <{DASHB.createdBy}> ?user .
            }}
        '''
        result = list(self.graph.query(qry))

        return pd.DataFrame({
            'dashboard': [str(row.dashboard) for row in result],
            'u_id': [str(row.user) for row in result],
            'i_id': [str(row.item) for row in result],
            'c_id': [str(row.context) for row in result]
        })
