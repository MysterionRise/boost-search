from datasets import load_dataset, load_metric
from transformers import DistilBertTokenizerFast
from transformers import AutoModelForSequenceClassification, DataCollatorWithPadding
from transformers import Trainer, TrainingArguments

checkpoint = "distilbert-base-uncased"

dataset = load_dataset("boolq")

print(dataset["train"].data)

tokenizer = DistilBertTokenizerFast.from_pretrained(checkpoint)


def tokenize(example):
    encoded = tokenizer(example["question"], example["passage"], truncation=True)
    encoded["labels"] = [int(a) for a in example["answer"]]
    return encoded


tokenized_datasets = dataset.map(tokenize, batched=True)
data_collator = DataCollatorWithPadding(tokenizer=tokenizer)
model = AutoModelForSequenceClassification.from_pretrained(checkpoint, num_labels=2)

args = TrainingArguments("roberta-booql",
                         per_device_train_batch_size=16,
                         learning_rate=1e-3,
                         output_dir="./results",
                         num_train_epochs=3)

trainer = Trainer(model,
                  args,
                  train_dataset=tokenized_datasets["train"],
                  eval_dataset=tokenized_datasets["validation"],
                  data_collator=data_collator,
                  tokenizer=tokenizer, )

trainer.train()

trainer.save_model("./saved_model")


