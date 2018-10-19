from bs4 import BeautifulSoup
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
file_handler = logging.FileHandler(filename='main.log')
stdout_handler = logging.StreamHandler(sys.stdout)
handlers = [file_handler, stdout_handler]
logging.basicConfig(
    level=logging.INFO,
	format='[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


def preprocess(str, porter):
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


def export_article(article_id, webpage_content, output_dir):
    porter = nltk.PorterStemmer()
    soup = BeautifulSoup(webpage_content, 'html.parser')
    paragraphs = soup.find_all('p')

    if paragraphs:
        f = open(os.path.join(output_dir, str(article_id) + '.txt'))
        for paragraph in paragraphs:
            f.write('%s\n' %preprocess(paragraph, porter))
        f.close()


def main():
    #article = NewsPlease.from_url(url)
    #print(article.text)

    # Initiate a directory to store the processed articles
    articles_dir = './articles'
    if not os.path.exists(articles_dir):
        os.makedirs(articles_dir)

    # Import information of articles as dataframe
    logger.info("Start crawling and processing articles...")
    articles_df = pd.read_csv("input/train.csv", index_col=-0)
    for article_id, article_info in articles_df.iterrows():
        try:
            r = requests.get(article_info["url"], timeout=10.0)
        except Exception as err:
            logger.exception(err)
            continue

        if r.status_code == 200:
            export_article(article_id, r.text, articles_dir)



if __name__ == "__main__":
    main()
