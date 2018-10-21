import os
import logging
import pandas as pd

logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

def main():
    articles_dir = "./output"

    logger.info("Loading processed articles and their labels.")


if __name__ == "__main__":
    main()
