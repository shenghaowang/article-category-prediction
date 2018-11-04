import os
import logging
import numpy as np
import pandas as pd
import xgboost
import time
from logging.config import fileConfig
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import KFold
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import (classification_report, accuracy_score,
                             precision_score, recall_score, f1_score)

logging.config.fileConfig(fname="logging.conf",
                          disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def main():
    articles_dir = "./output"

    logger.info("Loading article titles and their labels.")
    articles_info_df = pd.read_csv('input/train_v2.csv',
                                   index_col='article_id')
    article_bodies = []
    article_classes = []
    for article in os.listdir(articles_dir):
        article_id = article.split('.')[0]
        if article_id.isdigit():
            with open(os.path.join(articles_dir, article), 'r') as f:
                paragraphs = f.readlines()
            f.close()
            article_bodies.append(' '.join(paragraphs))
            article_classes.append(articles_info_df.loc[int(article_id), 'category'])

    logger.info("Constructing TF-IDF matrix for articles.")
    x = TfidfVectorizer().fit_transform(article_bodies)
    y = np.array(article_classes)

    logger.info("Dimension of TF-IDF matrix: %s", x.shape)
    logger.info("Start training classifier...")
    kf = KFold(n_splits=10)
    avg_a = 0
    avg_p = 0
    avg_r = 0
    avg_f1 = 0
    start_time = time.time()
    for train, test in kf.split(x):
        #model = MultinomialNB().fit(x[train], y[train])
        model = xgboost.XGBClassifier(max_depth=5, learning_rate=0.1,
                                      n_estimators=140).fit(x[train], y[train])
        predicts = model.predict(x[test])
        logger.info(classification_report(y[test], predicts))
        avg_a += accuracy_score(y[test], predicts)
        avg_p += precision_score(y[test],predicts, average='macro')
        avg_r += recall_score(y[test],predicts, average='macro')
        avg_f1 += f1_score(y[test],predicts, average='macro')

    logger.info('Average Accuracy is %f.' %(avg_a/10.0))
    logger.info('Average Precision is %f.' %(avg_p/10.0))
    logger.info('Average Recall is %f.' %(avg_r/10.0))
    logger.info('Average F1 score is %f.' %(avg_f1/10.0))
    logger.info("Elapsed time: %s seconds...",
                round(time.time() - start_time, 4))


if __name__ == "__main__":
    main()
