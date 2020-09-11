from pathlib import Path

from haystack.retriever.sparse import ElasticsearchRetriever
from haystack import Finder
from haystack.indexing.cleaning import clean_wiki_text
from haystack.indexing.utils import convert_files_to_dicts, fetch_archive_from_http
from haystack.reader.farm import FARMReader
from haystack.reader.transformers import TransformersReader
from haystack.utils import print_answers

from haystack.database.elasticsearch import ElasticsearchDocumentStore

if __name__ == '__main__':
    document_store = ElasticsearchDocumentStore(host="localhost", username="admin", password="admin", scheme="https",
                                                index="sec", verify_certs=False)

    retriever = ElasticsearchRetriever(document_store=document_store)

    # from farm.modeling.adaptive_model import AdaptiveModel
    # model = AdaptiveModel.convert_from_transformers('bert-base-uncased', device="cpu", task_type="question_answering")
    # farm_model_dir = Path("/Users/konstantinp/Downloads/bert-base-uncased")
    # model.save(farm_model_dir)
    # deepset/roberta-base-squad2
    # distilbert-base-uncased-distilled-squad
    # deepset/bert-large-uncased-whole-word-masking-squad2
    # ahotrod/electra_large_discriminator_squad2_512
    # mfeb/albert-xxlarge-v2-squad2
    reader = FARMReader(model_name_or_path="deepset/bert-large-uncased-whole-word-masking-squad2", use_gpu=False)
    # reader.save("/Users/konstantinp/Downloads/bert-base-uncased")
    finder = Finder(reader, retriever)

    prediction = finder.get_answers(question="Who is Oleg Vilchinski?", top_k_retriever=10, top_k_reader=5)

    print_answers(prediction, details="minimal")

    prediction = finder.get_answers(question="What is Regeneron?", top_k_retriever=10, top_k_reader=5)

    print_answers(prediction, details="minimal")

    prediction = finder.get_answers(question="Where Veller works?", top_k_retriever=10, top_k_reader=5)

    print_answers(prediction, details="minimal")

    prediction = finder.get_answers(question="How I could use AWS Lambda?", top_k_retriever=10, top_k_reader=5)

    print_answers(prediction, details="minimal")

# todo don't do clean up as in wiki
# todo list of models? check different models
# todo change the way to process original data
#
