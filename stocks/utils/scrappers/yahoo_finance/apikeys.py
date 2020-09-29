import os
import logging


logging.basicConfig(level=logging.ERROR, format=f'%(asctime)s | %(levelname)s | %(funcName)s | %(message)s')
logger = logging.getLogger(__name__)

def load():
    keys_dir = "./keys"
    keys = []
    if not os.path.exists(keys_dir):
        logger.debug("Creating keys directory")
        os.mkdir(keys_dir)
    else:
        for file in os.listdir(keys_dir):
            keys.append(file)
    return keys