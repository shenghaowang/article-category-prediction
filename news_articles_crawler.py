import os
import requests
import logging
import sys
import time
import pandas as pd
from logging.config import fileConfig
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from threading import Thread
from queue import Queue
from socket import gaierror
from urllib3.exceptions import (NewConnectionError, MaxRetryError,
ReadTimeoutError, ProtocolError)
from requests.exceptions import ConnectionError, ReadTimeout, TooManyRedirects


logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def scrape_worker(queue, dir):
    """Scrape news articles from webpages and save as text files.

    Args:
        queue (Queue): queue of the crawling tasks.
        dir (str): Directory which stores the raw articles.

    """
    while not queue.empty():
        # Fetch new crawling task from the queue
        article_info = queue.get()
        try:
            r = requests.get(article_info['url'], timeout=10.0)
        except (gaierror, ConnectionError, NewConnectionError, MaxRetryError,
               ReadTimeoutError, ProtocolError, ReadTimeout, TooManyRedirects) as err:
            logger.error("%s occurs to article %s", sys.exc_info()[0], article_info['article_id'])
            queue.task_done()
            #continue

        if r.status_code == 200:
            soup = BeautifulSoup(r.text, 'html.parser')
            ps = soup.find_all('p')
            if ps:
                f = open(os.path.join(dir, str(article_info['article_id']) + '.txt'), 'w')
                for p in ps:
                    f.write('%s\n' %p)
                logger.info("Article %s processed.", article_info['article_id'])
                f.close()
        queue.task_done()


def main():
    """Main function which facilitates the crawling task.
    """
    # Initiate a directory to store the raw html pages with article
    raw_dir = './raw'
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    # Import information of articles as dataframe
    logger.info("Start crawling news articles...")
    articles_df = pd.read_csv("input/train.csv")

    # Convert it to a list of dictionaries
    article_dicts = articles_df.to_dict(orient='records')

    # Load up the queue with the articles to crawl
    q = Queue()
    #map(q.put, article_dicts)
    for article_dict in article_dicts:
        q.put(article_dict)

    # Initiate multithreaded crawling
    no_of_workers = 5
    start_time = time.time()
    for i in range(no_of_workers):
        logger.debug("Start thread %s", i)
        worker = Thread(target=scrape_worker, args=(q, raw_dir))
        worker.setDaemon(True)
        worker.start()

    # Wait until the queue has been processed
    q.join()

    logger.info("%s out of %s articles have been scraped.",
                len(os.listdir(raw_dir)), len(article_dicts))
    logger.info("Elapsed time: %s seconds...",
                round(time.time() - start_time, 4))


if __name__ == "__main__":
    main()
