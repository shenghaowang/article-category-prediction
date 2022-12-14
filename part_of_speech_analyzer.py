from textblob import TextBlob
from logging.config import fileConfig
import os
import time
import logging
import pandas as pd

# Set up logging config
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)

pos_family = {
    'noun' : ['NN','NNS','NNP','NNPS'],
    'pron' : ['PRP','PRP$','WP','WP$'],
    'verb' : ['VB','VBD','VBG','VBN','VBP','VBZ'],
    'adj' :  ['JJ','JJR','JJS'],
    'adv' : ['RB','RBR','RBS','WRB']
}

# Count part of speech tag in a given article
def check_pos_tag(text, flag):
    cnt = 0
    try:
        wiki = TextBlob(text)
        for tup in wiki.tags:
            ppo = list(tup)[1]
            if ppo in pos_family[flag]:
                cnt += 1
    except:
        pass
    return cnt


def main():
    #articles_dir = './output'
    articles_dir = './output_test'
    features_dir = './features'
    n_articles = len(os.listdir(articles_dir))
    part_of_speech_features = []
    article_count = 0

    logger.info("Loading article body and extract features.")
    start_time = time.time()
    for article in os.listdir(articles_dir):
        article_id = article.split('.')[0]
        if article_id.isdigit():
            with open(os.path.join(articles_dir, article), 'r') as f:
                paragraphs = f.readlines()
            f.close()
            if paragraphs:
                article_body = ' '.join(paragraphs)
                part_of_speech = {}
                word_bag = []
                for paragraph in paragraphs:
                    words = paragraph.split(' ')
                    word_bag.extend(words)
                part_of_speech['article_id'] = article_id
                part_of_speech['char_count'] = sum([len(word) for word in word_bag])
                part_of_speech['word_count'] = len(article_body.split(' '))
                part_of_speech['paragraph_count'] = len(paragraphs)
                part_of_speech['noun_count'] = check_pos_tag(article_body, 'noun')
                part_of_speech['verb_count'] = check_pos_tag(article_body, 'verb')
                part_of_speech['adj_count'] = check_pos_tag(article_body, 'adj')
                part_of_speech['adv_count'] = check_pos_tag(article_body, 'adv')
                part_of_speech['pron_count'] = check_pos_tag(article_body, 'pron')
                part_of_speech_features.append(part_of_speech)

            article_count += 1
            if article_count % 100 == 0:
                logger.info("Features of %s out of %s articles have been extracted.",
                            article_count, n_articles)

    # Write part of speech features into file
    if not os.path.exists(features_dir):
        os.makedirs(features_dir)
    num_valid_articles = len(part_of_speech_features)
    part_of_speech_df = pd.DataFrame(part_of_speech_features,
                                     columns=['article_id', 'char_count', 'word_count',
                                              'paragraph_count', 'noun_count', 'verb_count',
                                              'adj_count', 'adv_count', 'pron_count'],
                                     index=list(range(num_valid_articles)))
    part_of_speech_df = part_of_speech_df.sort_values(by=['article_id'])
    part_of_speech_df.to_csv(os.path.join(features_dir, 'part_of_speech_test.csv'), index=False)
    logger.info("Part of speech features have been written in file.")
    logger.info("Elapsed time: %s seconds...",
                round(time.time() - start_time, 4))

if __name__ == "__main__":
    main()
