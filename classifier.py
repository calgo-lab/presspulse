import os
import pandas as pd
import torch
from datasets import Dataset
from transformers import (
    AutoModelForSequenceClassification,
    AutoTokenizer,
    DataCollatorWithPadding,
    Trainer,
    TrainingArguments,
)

model_path = "/volume/output/model"
lable = "/volume/output/predict/label_codes_with_index.csv"

_trainer = None
_tokenizer = None
_index_to_label = None


def _load():
    global _trainer, _tokenizer, _index_to_label

    model = AutoModelForSequenceClassification.from_pretrained(model_path)
    _tokenizer = AutoTokenizer.from_pretrained(model_path)

    label_mapping = pd.read_csv(lable)
    _index_to_label = label_mapping["new_label"].to_dict()

    training_args = TrainingArguments(
        output_dir="prediction_trainer",
        per_device_eval_batch_size=32,
        fp16=torch.cuda.is_available(),  
        do_train=False,
        do_eval=False,
        remove_unused_columns=False,
    )

    _trainer = Trainer(
        model=model,
        args=training_args,
        #tokenizer=_tokenizer,
        data_collator=DataCollatorWithPadding(_tokenizer),
    )


def classify(entries: list[dict]) -> list[dict]:
    if _trainer is None:
        _load()

    texts = [e["text"] for e in entries]

    tokenized = _tokenizer(
        texts,
        padding=True,
        truncation=True,
        return_tensors=None,
        max_length=512,
    )
    dataset = Dataset.from_dict(tokenized)

    predictions = _trainer.predict(dataset)
    probs = torch.softmax(torch.tensor(predictions.predictions).float(), dim=-1).tolist()

    for entry, prob in zip(entries, probs):
        all_scores = {_index_to_label[i]: round(p * 100, 2) for i, p in enumerate(prob)}
        top_label = max(all_scores, key=all_scores.get)
        entry["label"] = top_label
        entry["score"] = all_scores[top_label]
        entry["all_scores"] = all_scores

    return entries
