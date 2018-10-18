#from newsplease import NewsPlease
#import ssl
from bs4 import BeautifulSoup
import requests
import logging
import sys

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


def preprocess():
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

    def rm_hashtag_symbol(str):
        return re.sub(r'#', '', str)

    def replace_emoticon(emoticon_dict, str):
        for k, v in emoticon_dict.items():
            str = str.replace(k, v)
        return str


def main():
    url = "https://www.nasdaq.com/article/forex-pound-drops-to-onemonth-lows-against-euro-cm333750"
    #url = "https://www.nytimes.com/2017/02/23/us/politics/cpac-stephen-bannon-reince-priebus.html?hp"
    #article = NewsPlease.from_url(url)
    #print(article.text)

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    ps = soup.find_all('p')
    #logger.info(ps)

    if ps:
        for p in ps:


if __name__ == "__main__":
    main()
