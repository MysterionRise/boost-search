from pathlib import Path

from farm.modeling.adaptive_model import AdaptiveModel
from haystack.reader.farm import FARMReader

if __name__ == '__main__':
    models = [
        "deepset/roberta-base-squad2",
        "distilbert-base-uncased-distilled-squad",
        "deepset/bert-large-uncased-whole-word-masking-squad2",
        "ahotrod/electra_large_discriminator_squad2_512",
        "mfeb/albert-xxlarge-v2-squad2"
    ]
    for model_name in models:
        model = AdaptiveModel.convert_from_transformers(model_name, device="cpu", task_type="question_answering")
        reader = FARMReader(model_name_or_path=model_name, use_gpu=False)
        farm_model_dir = Path("/Users/konstantinp/projects/boost-search/haystack/data/models/{}".format(model_name))
        reader.save(farm_model_dir)

# todo don't do clean up as in wiki
# todo list of models? check different models
# todo change the way to process original data
#
