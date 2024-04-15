import config_ini
import logging
import torch

log = logging.getLogger(config_ini.LOGGING_CONF)


class Model(object):
    def __init__(self):
        log.debug("Model device init")
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        log.debug(f"Model device: {self.device}")
