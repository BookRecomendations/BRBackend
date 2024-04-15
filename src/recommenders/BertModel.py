import config_ini
import logging
from transformers import AutoTokenizer, AutoModel
from torch import torch
from .Model import Model

log = logging.getLogger(config_ini.LOGGING_CONF)


class BertModel(Model):
    def __init__(self, model_name: str = 'bert-base-uncased'):
        super().__init__()
        log.debug("BertModel init")
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)

    def train(self):
        log.debug("BertModel train")
        pass

    def get_tokens(self, text: str):
        log.debug("BertModel get_tokens")
        return self.tokenizer.encode(text, return_tensors='pt', max_length=512, truncation=True).to(self.device)

    def get_embedding(self, text: str):
        log.debug("BertModel get_embedding")
        input_ids = self.get_tokens(text)
        with torch.no_grad():
            return self.model(input_ids).last_hidden_state.mean(dim=1).squeeze().cpu().numpy()