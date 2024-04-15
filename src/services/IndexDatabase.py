import logging
import os.path
from typing import Literal, List

import numpy as np
from annoy import AnnoyIndex

import config_ini

log = logging.getLogger(config_ini.LOGGING_CONF)


class IndexDatabase:
    def __init__(self, metric: Literal["angular", "euclidean", "manhattan", "hamming", "dot"] = "angular",
                 vector_size: int = 512, name: str = "index"):
        self.name = name
        self.tree_number = 10
        self.vector_size = vector_size
        self.metric = metric
        self.index = AnnoyIndex(vector_size, metric)
        self.index.set_seed(308171)

    def add_item(self, item: int, vector: np.ndarray):
        self.index.add_item(item, vector)

    def build(self):
        self.index.build(self.tree_number)

    def get_nns_by_vector(self, vector: np.ndarray, n: int) -> List[int]:
        return self.index.get_nns_by_vector(vector, n)

    def get_item_vector(self, item: int) -> list[float]:
        return self.index.get_item_vector(item)

    def get_nns_by_item(self, item: int, n: int) -> List[int]:
        return self.index.get_nns_by_item(item, n)

    def save(self, path: str, replace: bool = False):
        # add the name to the path
        full_path = os.path.join(path, self.name)

        # add the extension to the path
        full_path = full_path + ".ann"

        if os.path.exists(full_path) and not replace:
            raise FileExistsError(f"Index {self.name} already exists at {full_path}")

        log.debug(f"Saving index {self.name} to {full_path}")
        self.index.save(full_path)
        log.debug(f"Saved index {self.name} to {full_path}")

    def load(self, path: str):
        log.debug(f"Loading index {self.name} from {path}")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Index {self.name} not found at {path}")

        self.index.load(path)
        log.debug(f"Loaded index {self.name} from {path}")
