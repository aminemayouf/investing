import os
import logging


logger = logging.getLogger()

def get_api_keys():
    keys_dir = "./keys"
    keys = []
    if not os.path.exists(keys_dir):
        logger.debug("Creating keys directory")
        os.mkdir(keys_dir)
    else:
        for file in os.listdir(keys_dir):
            keys.append(file)
    return keys