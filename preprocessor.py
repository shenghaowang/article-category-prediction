from nltk.corpus import stopwords
import os
import re
import nltk
import requests
import logging
import sys
import time
import pandas as pd

#from newsplease import NewsPlease
#import ssl

#ssl._create_default_https_context = ssl._create_unverified_context
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def pre_process(str, porter):
    """Remove
    """
    def rm_html_tags(str):
        html_prog = re.compile(r'<[^>]+>',re.S)
        return html_prog.sub('', str)

    def rm_html_escape_characters(str):
        pattern_str = r'&quot;|&amp;|&lt;|&gt;|&nbsp;|&#34;|&#38;|&#60;|&#62;|&#160;|&#20284;|&#30524;|&#26684|&#43;|&#20540|&#23612;'
        escape_characters_prog = re.compile(pattern_str, re.S)
        return escape_characters_prog.sub('', str)

    def rm_at_user(str):
        return re.sub(r'@[a-zA-Z_0-9]*', '', str)

    def rm_url(str):
        return re.sub(r'http[s]?:[/+]?[a-zA-Z0-9_\.\/]*', '', str)

    def rm_repeat_chars(str):
        return re.sub(r'(.)(\1){2,}', r'\1\1', str)

    def rm_hashtag_symbol(str):
        return re.sub(r'#', '', str)

    def rm_time(str):
        return re.sub(r'[0-9][0-9]:[0-9][0-9]', '', str)

    def rm_punctuation(str):
        return re.sub(r'[^\w\s]','' ,str)

    str = str.lower()
    str = rm_url(str)
    str = rm_at_user(str)
    str = rm_repeat_chars(str)
    str = rm_hashtag_symbol(str)
    str = rm_time(str)
    str = rm_punctuation(str)

    try:
        str = nltk.tokenize.word_tokenize(str.strip())
        try:
            str = [porter.stem(t) for t in str]
        except:
            pass
    except:
        pass

    return str


def main():
    """
    """
    articles_dir = './raw'
    output_dir = './output'
    if not os.path.exists(articles_dir):
        os.makedirs(output_dir)
    porter = nltk.PorterStemmer()
    stops = set(stopwords.words('english'))

    logger.info("Start loading and processing sampels...")
    words_stat = {}
    processed_articles = {}
    for raw_article in os.listdir(articles_dir):
        logger.info("Processing article %s", article_id)
        article_id = raw_article.split('.')[0]
        paragraphs = []
        with open(os.path.join(articles_dir, raw_article), 'r') as f:
            for i, line in enumerate(f):
                processed_words = []
                paragraph = line.replace("\n", " ")
                words = pre_process(paragraph, porter)
                for word in words:
                    if word not in stops:
                        processed_words.append(word)
                        # Record statistics of the df and tf for each word
                        # Format: {word: [tf, df, article index]
                        if word in words_stat.keys():
                            words_stat[word][0] += 1
                            if i != words_stat[word][2]:
                                words_stat[word][1] += 1
                                words_stat[word][2] = i
                        else:
                            words_stat[word] = [1, 1, i]
                paragraphs.append(' '.join(processed_words))
        f.close()
        processed_articles[article_id] = paragraphs

    # Save the statistics of td and df for each words into file
    logger.info("The number of unique words in the articles is %s.", len(words_stat.keys()))
    lowTF_words = set()
    stats_dir = "./stats"
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)

    with open(os.path.join(stats_dir, "article_words_statistics.txt"), 'w') as f_stat:
        f_stat.write("TF\tDF\tWORD\n")
        for word, stat in sorted(words_stat.items(), key=lambda i: i[1], reverse=True):
            f_stat.write('\t'.join([str(m) for m in stat[0:2]]) + '\t' + word +  '\n')
            if stat[0] < 2:
                lowTF_words.add(word)
    f_stat.close()
    logger.info("The number of low frequency words is %s.", len(lowTF_words))

    # Filter the low frequecy words in the articles
    for article_id in processed_articles.keys():
        f_out = open(os.path.join(output, str(article_id) + ".txt"), 'w')
        for paragraph in processed_articles[article_id]:
            words = paragraph.split(' ')
            filtered_words = []
            for word in words:
                if word not in lowTF_words:
                    filtered_words.append(word)
            processed_paragraph = ' '.join(filtered_words)
            f_out.write('%s\n' %processed_paragraph)
        f_out.close()
        logger.info("Article %s has been preprocessed.", article_id)


if __name__ == "__main__":
    main()
