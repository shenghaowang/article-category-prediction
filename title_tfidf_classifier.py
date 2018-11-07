import os
import logging
import numpy as np
import pandas as pd
import time
from logging.config import fileConfig
from xgboost import XGBClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import KFold
#from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import (classification_report, accuracy_score,
                             precision_score, recall_score, f1_score)

logging.config.fileConfig(fname="logging.conf",
                          disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def main():
    #articles_dir = "./output"

    logger.info("Loading article titles and their labels.")
    articles_info_df = pd.read_csv('input/train_v2.csv',
                                   index_col='article_id')
    article_titles = articles_info_df['title'].tolist()
    article_classes = articles_info_df['category'].tolist()

    logger.info("Constructing TF-IDF matrix for articles.")
    x = TfidfVectorizer().fit_transform(article_titles)
    y = np.array(article_classes)

    logger.info("Dimension of TF-IDF matrix: %s", x.shape)
    logger.info("Start training classifier...")
    kf = KFold(n_splits=10)
    avg_a = 0
    avg_p = 0
    avg_r = 0
    avg_f1 = 0
    start_time = time.time()

    # Split training and validation datasets
    x_train, x_val, y_train, y_val = train_test_split(x, y, test_size = .2,
                                                      random_state=12, stratify=y)
    #model = MultinomialNB().fit(x[train], y[train])
    model1 = XGBClassifier(max_depth=5, learning_rate=0.1,
                           n_estimators=140).fit(x_train, y_train)
    predicts = model1.predict(x_val)
    logger.info("Precision: %s" %round(precision_score(y_val, predicts, average='macro'), 4))
    logger.info("Recall: %s" %round(recall_score(y_val, predicts, average='macro'), 4))
    logger.info("F1 score: %s" %round(f1_score(y_val, predicts, average='macro'), 4))
    logger.info("Accuracy: %s" %round(accuracy_score(y_val, predicts), 4))

    logger.info("Elapsed time: %s seconds...",
                round(time.time() - start_time, 4))


if __name__ == "__main__":
    main()
