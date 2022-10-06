import copy
import gzip
import os
import pickle

from rdflib import Graph

from viscars.recommenders import Recommender


class CF(Recommender):
    def __init__(self, graph: Graph, verbose=False):
        super().__init__(graph, verbose)

    def _build_model(self):
        with gzip.open(os.path.join('D:\\Documents\\UGent\\PhD\\projects\\PhD\\VisCARS\\data\\protego\\output', 'RDF2VecCC.json.pkl.gzip'), 'rb') as input_f:
            self.cc_similarities = pickle.load(input_f)

    def kneighbours_cc(self, uid, cid, iid, k=20, strict=True):
        cc_similarities_ = copy.deepcopy(self.cc_similarities)

        if strict:
            for c, w in self.cc_similarities[cid].items():
                qry = f'''
                    PREFIX dashb: <http://dynamicdashboard.ilabt.imec.be/broker/ontologies/dashboard#>
                    PREFIX sosa: <http://www.w3.org/ns/sosa/>
                    PREFIX ssn-ext: <http://dynamicdashboard.ilabt.imec.be/broker/ontologies/ssn-extension/>

                    SELECT * WHERE {{
                        ?widget a dashb:Widget ;
                            dashb:createdBy <{uid}> ;
                            dashb:hasProperty ?property .

                        ?sensor ssn-ext:subSystemOf <{c}> ;
                            sosa:observes ?property .
                    }}
                '''
                if len(list(self.graph.query(qry))) == 0:
                    cc_similarities_[cid].pop(c)

        if cid in cc_similarities_[cid].keys():
            cc_similarities_[cid].pop(cid)

        return sorted(cc_similarities_[cid].items(), key=lambda x: x[1])[:k]

    # def kneighbours_ii(self, iid, k=20):
    #     ii_similarities_ = copy.deepcopy(ii_similarities)
    #     ii_similarities_[iid].pop(uid)
    #     return sorted(ii_similarities_[iid].items(), key=lambda x: x[1])[:k]
    #
    # def kneighbours_uu(self, uid, cid, iid, k=20, strict=True):
    #     uu_similarities_ = copy.deepcopy(uu_similarities)
    #
    #     if strict:
    #         for u, w in uu_similarities[uid].items():
    #             qry = f'''
    #                 PREFIX dashb: <http://dynamicdashboard.ilabt.imec.be/broker/ontologies/dashboard#>
    #
    #                 SELECT * WHERE {{
    #                     ?widget a dashb:Widget ;
    #                         dashb:createdBy <{u}> ;
    #                         dashb:hasProperty <{iid}> .
    #                 }}
    #             '''
    #             if len(list(self.graph.query(qry))) == 0:
    #                 uu_similarities_[uid].pop(u)
    #
    #     if uid in uu_similarities_[uid].keys():
    #         uu_similarities_[uid].pop(uid)
    #
    #     return sorted(uu_similarities_[uid].items(), key=lambda x: x[1])[:k]
    #
    # def predict_uucf(self, uid, cid, iid):
    #     # Calculate K-nearest neighbours of the user
    #     neighbours = self.kneighbours_uu(uid, cid, iid)
    #
    #     total_rw = 0
    #     total_w = 0
    #     for n, w in neighbours:
    #         # Get ratings from user n for item i
    #         qry = f'''
    #             PREFIX dashb:<http://dynamicdashboard.ilabt.imec.be/broker/ontologies/dashboard#>
    #
    #             SELECT * WHERE {{
    #                 ?widget a dashb:Widget ;
    #                     dashb:createdBy <{n}> ;
    #                     dashb:hasProperty <{iid}> .
    #             }}
    #         '''
    #         r_aui = 1 if len(list(self.graph.query(qry))) > 0 else 0
    #         w_au = w  # Similarity score of user u and user n
    #         total_rw += r_aui * w_au
    #         total_w += w
    #     return total_rw / total_w if total_w > 0 else 0

    def predict_cccf(self, uid, cid, iid):
        # Calculate K-nearest neighbours of the patient
        neighbours = self.kneighbours_cc(uid, cid, iid)

        total_rw = 0
        total_w = 0
        for n, w in neighbours:
            # Get ratings from user i for similar items (metric-based) of patient n
            qry = f'''
                PREFIX dashb: <http://dynamicdashboard.ilabt.imec.be/broker/ontologies/dashboard#>
                PREFIX sosa: <http://www.w3.org/ns/sosa/>
                PREFIX ssn-ext: <http://dynamicdashboard.ilabt.imec.be/broker/ontologies/ssn-extension/>

                SELECT * WHERE {{
                    <{iid}> dashb:produces ?metric .

                    ?sensor ssn-ext:subSystemOf <{n}> ;
                        sosa:observes ?property .
                    ?property dashb:produces ?metric .

                    ?widget a dashb:Widget ;
                        dashb:createdBy <{uid}> ;
                        dashb:hasProperty ?property .
                }}
            '''
            r_aui = 1 if len(list(self.graph.query(qry))) > 0 else 0
            w_au = w  # Similarity score of patient cid and patient n
            total_rw += r_aui * w_au
            total_w += w
        return total_rw / total_w if total_w > 0 else 0

    def predict(self, uid, cid, *kwargs):
        # Get all items from the patient
        qry = f'''
            PREFIX dashb: <http://dynamicdashboard.ilabt.imec.be/broker/ontologies/dashboard#>
            PREFIX sosa: <http://www.w3.org/ns/sosa/>
            PREFIX ssn-ext: <http://dynamicdashboard.ilabt.imec.be/broker/ontologies/ssn-extension/>

            SELECT ?property WHERE {{
                ?sensor ssn-ext:subSystemOf <{cid}> ;
                    sosa:observes ?property .
            }}
        '''
        items = [str(property_[0]) for property_ in self.graph.query(qry)]

        scores = {}
        for iid in items:
            scores[iid] = self.predict_cccf(uid, cid, iid)

        recommendations = [{'contextId': cid, 'itemId': item, 'score': score} for item, score in scores.items()]
        return sorted(recommendations, key=lambda n: n['score'], reverse=True)

    def top_n(self, uid: [], cid: [], n: int, **kwargs):
        pass


if __name__ == '__main__':
    graph_ = Graph()
    graph_.parse('D:\\Documents\\UGent\\PhD\\projects\\PhD\\VisCARS\\data\\protego\\protego_zplus.ttl')
    graph_.parse('D:\\Documents\\UGent\\PhD\\projects\\PhD\\VisCARS\\data\\protego\\protego_ddashboard.ttl')
    recommender = CF(graph_)

    print(recommender.predict('https://dynamicdashboard.ilabt.imec.be/users/10', 'http://example.com/tx/patients/zplus_6'))
