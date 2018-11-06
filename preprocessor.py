import os
import re
import nltk
import logging
import time
from nltk.corpus import stopwords
from logging.config import fileConfig


#ssl._create_default_https_context = ssl._create_unverified_context
logging.config.fileConfig(fname="logging.conf", disable_existing_loggers=False)
logger = logging.getLogger(__name__)


def pre_process(str, porter):
    """Remove irrelevant characters and symbols

    Args:
        str (str): Word in articles to be processed.
        porter (PorterStemmer): Stemmer used to remove morphological affixes
            from words, leaving only the word stem.

    Return:
        str (str): Word segment after being processed.

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

    def rm_digits(str):
        return re.sub('^[0-9 ]+', '', str)

    str = str.lower()
    str = rm_html_tags(str)
    str = rm_html_escape_characters(str)
    str = rm_url(str)
    str = rm_at_user(str)
    str = rm_repeat_chars(str)
    str = rm_hashtag_symbol(str)
    str = rm_time(str)
    str = rm_punctuation(str)
    str = rm_digits(str)

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
    """Main function which performs preprocessing and extracts the term frequency
    and document frequency of words in articles.

    """
    #articles_dir = './raw'
    articles_dir = 'notebook/raw_test_new'
    output_dir = './output_test'

    # Create folder to store output if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        # Remove all files from the folder
        for article in os.listdir(output_dir):
            article_path = os.path.join(output_dir, article)
            try:
                if os.path.isfile(article_path):
                    os.unlink(article_path)
            except Exeception as err:
                logger.error("Error occurred when removing existing processed articles.")
    porter = nltk.PorterStemmer()
    stops = set(stopwords.words('english'))
    num_articles = len(os.listdir(articles_dir))

    logger.info("Start loading and processing samples...")
    logger.info("In total %s articles to be processed...", num_articles)
    words_stat = {}
    processed_articles = {}
    article_count = 0
    start_time = time.time()
    for raw_article in os.listdir(articles_dir):
        article_id = raw_article.split('.')[0]
        paragraphs = []
        if article_id.isdigit():
            with open(os.path.join(articles_dir, raw_article), 'r',
                     encoding='ISO-8859-1') as f:
                for i, line in enumerate(f):
                    processed_words = []
                    paragraph = line.replace("\n", " ")
                    words = pre_process(paragraph, porter)
                    if words:
                        #for word in words.split(' '):
                        for word in words:
                            word = word.strip()
                            if word and word not in stops:
                                processed_words.append(word)
                                # Record statistics of the df and tf for each word
                                # Format: {word: [tf, df, article index]
                                if word in words_stat.keys():
                                    words_stat[word][0] += 1
                                    if article_id != words_stat[word][2]:
                                        words_stat[word][1] += 1
                                        words_stat[word][2] = article_id
                                else:
                                    words_stat[word] = [1, 1, article_id]
                        paragraphs.append(' '.join(processed_words))
            f.close()
            processed_articles[article_id] = paragraphs
            article_count += 1
            if article_count % 100 == 0:
                logger.info("%s out of %s articles have been processed.",
                            article_count, num_articles)
                #logger.info(paragraphs)

    # Save the statistics of td and df for each words into file
    logger.info("The number of unique words in the articles is %s.", len(words_stat.keys()))
    lowTF_words = set()
    with open("article_words_statistics.txt", 'w') as f_stat:
        f_stat.write("TF\tDF\tWORD\n")
        for word, stat in sorted(words_stat.items(), key=lambda i: i[1], reverse=True):
            f_stat.write('\t'.join([str(m) for m in stat[0:2]]) + '\t' + word +  '\n')
            if stat[0] < 2:
                lowTF_words.add(word)
    f_stat.close()
    logger.info("The number of low frequency words is %s.", len(lowTF_words))

    # Filter the low frequecy words and export the articles
    for article_id in processed_articles.keys():
        f_out = open(os.path.join(output_dir, str(article_id) + ".txt"), 'w')
        for paragraph in processed_articles[article_id]:
            words = paragraph.split(' ')
            filtered_words = []
            for word in words:
                if word and word not in lowTF_words:
                    filtered_words.append(word)

            if filtered_words:
                processed_paragraph = ' '.join(filtered_words)
                f_out.write('%s\n' %processed_paragraph)
        f_out.close()

    logger.info("All articles have been preprocessed.")
    logger.info("Elapsed time: %s seconds...",
                round(time.time() - start_time, 4))


if __name__ == "__main__":
    main()
