# from src.recommenders.BertModel import BertModel
#
# model = BertModel()
# tokens = model.get_tokens(
#     "Grandpa Pig buys George a dinosaur balloon but George keeps letting it go. Who will rescue the balloon when it starts to float away?\n A new adventure featuring Peppa and George.")
# print(tokens)
#
import torch

from transformers import AutoTokenizer, AutoModel

from src.services.IndexDatabase import IndexDatabase

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
# tokenizer = AutoTokenizer.from_pretrained("thenlper/gte-small")
# model = AutoModel.from_pretrained("thenlper/gte-small").to(device)
# fast_tokenizer = AutoTokenizer.from_pretrained("thenlper/gte-small")

text = ("Yet remarkably appearance get him his projection. Diverted endeavor bed peculiar men the not desirous. "
        "Acuteness abilities ask can offending furnished fulfilled sex. Warrant fifteen exposed ye at mistake. Blush "
        "since so in noisy still built up an again. As young ye hopes no he place means. Partiality diminution gay "
        "yet entreaties admiration. In mr it he mention perhaps attempt pointed suppose. Unknown ye chamber of "
        "warrant of norland arrived. Is education residence conveying so so. Suppose shyness say ten behaved morning "
        "had. Any unsatiable assistance compliment occasional too reasonably advantages. Unpleasing has ask "

        )

from sentence_transformers import SentenceTransformer
from sentence_transformers.util import cos_sim

sentences = ['That is a happy person', 'That is a very happy person']

model = SentenceTransformer('thenlper/gte-base')
embeddings = model.encode(sentences, show_progress_bar=True, convert_to_numpy=True).to(device)
print(embeddings)
print(cos_sim(embeddings[0], embeddings[1]))


# check if thext will fit in 512 tokens
# tokenizer.

# input_ids = tokenizer.encode(text,  max_length=512, padding='max_length', return_tensors='pt').to(device)
# with torch.no_grad():
#     print(model(input_ids).last_hidden_state.mean(dim=1).squeeze().cpu().numpy())
#
# # check if text has 512 tokens
# print(len(input_ids[0]))
# print(input_ids)
#
# print(tokenizer.decode(input_ids[0]))
#
# print(tokenizer(text, return_tensors='pt', max_length=512, padding='max_length', truncation=True))

# import torch
# from transformers import pipeline
#
# summarizer = pipeline(
#     "summarization",
#     "pszemraj/long-t5-tglobal-base-16384-book-summary",
#     device=0 if torch.cuda.is_available() else -1,
# )
# long_text = "Here is a lot of text I don't want to read. Replace me"
#
# result = summarizer(long_text)
# print(result[0]["summary_text"])

annoy = IndexDatabase(name="test")
# annoy.add_item()

