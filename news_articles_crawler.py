import os
import requests
import logging
import sys
import time
import pandas as pd
from threading import Thread
from queue import Queue

#import ssl
#ssl._create_default_https_context = ssl._create_unverified_context
file_handler = logging.FileHandler(filename='main.log')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
    level=logging.INFO,
	format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


def scrape_worker(queue, dir):
    """
    """
    while not queue.empty():
        article_info = queue.get()
        try:
            r = requests.get(article_info['url'], timeout=10.0)
        except Exception as err:
            logger.exception(err)
            queue.task_done()
            continue

        if r.status_code == 200:
            f = open(os.path.join(dir, article_info['id'] + '.txt'))
            f.write('%s' %r.text)
            f.close()
        queue.task_done()


def main():
    """
    """
    # Initiate a directory to store the raw html pages with article
    raw_dir = './raw'
    if not os.path.exists(raw_dir):
        os.makedirs(raw_dir)

    # Import information of articles as dataframe
    logger.info("Start crawling news articles...")
    articles_df = pd.read_csv("input/train.csv", index_col=-0)

    # Convert it to a list of dictionaries
    article_dicts = articles_df.to_dict()

    # Initiate multithreaded crawling
    no_of_workers = 5
    q = Queue()
    map(q.put, article_dicts)
    start_time = time.time()
    for i in range(no_of_workers):
        thread = Thread(target=scrape_worker, args=(q, raw_dir))
        thread.start()
    q.join()

    logger.info("%s out of %s articles have been scraped.",
                len(os.listdir(raw_dir)), len(article_dicts))
    logger.info("Elapsed time: %s seconds...",
                round(time.time() - start_time, 4))


if __name__ == "__main__":
    main()
