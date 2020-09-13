import logging
from typing import Dict, Any

from flask import g
from haystack import Finder
from haystack.database.elasticsearch import ElasticsearchDocumentStore
from haystack.reader.farm import FARMReader
from haystack.retriever.sparse import ElasticsearchRetriever
from haystack.utils import print_answers


def get_finder() -> Finder:
    if 'FINDER' not in g:
        logging.info('Initialising finder...')
        document_store = ElasticsearchDocumentStore(host="odfe-node", username="admin", password="admin",
                                                    scheme="https",
                                                    index="sec", verify_certs=False)

        retriever = ElasticsearchRetriever(document_store=document_store)
        reader = FARMReader(model_name_or_path="/tmp/data/models/deepset/roberta-base-squad2", use_gpu=False)
        g.finder = Finder(reader, retriever)
        logging.info('Initialising finder finished')
    return g.finder


def ask_question(question: str) -> Dict[str, Any]:
    # todo add as parameter - name of the model, both top_k
    prediction = get_finder().get_answers(question=question, top_k_retriever=10, top_k_reader=5)

    print_answers(prediction, details="minimal")
    return prediction['answers']
