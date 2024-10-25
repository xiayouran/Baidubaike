# -*- coding: utf-8 -*-
# Author  : liyanpeng
# Email   : yanpeng.li@cumt.edu.cn
# Datetime: 2024/10/22 12:30
# Filename: baike.py
import re
import requests
from bs4 import BeautifulSoup
from collections import OrderedDict
from typing import Union, Tuple

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from baidubaike.utils.error import DisambiguationError, PageError, VerifyError
from baidubaike.utils.proxy import get_random_proxy

__all__ = ['WordSearch', 'SearchbySelenium']

CLASS_DISAMBIGUATION = ['nslog:519']
CLASS_CREATOR = ['nslog:1022']
CLASS_REFERENCE = ['nslog:1968']
CLASS_TAG = ['nslog:7336', 'taglist']
CLASS_CONTENT = ['lemmaTitleH1', 'headline-1', 'headline-2', 'para']
CLASS_SUMARRY = ['lemmaSummary__tEeY J-summary']


class Page(object):

    def __init__(self, string, encoding='utf-8'):

        url = 'http://baike.baidu.com/search/word'
        payload = None

        # An url or a word to be Paged
        pattern = re.compile('^http:\/\/baike\.baidu\.com\/.*', re.IGNORECASE)
        if re.match(pattern, string):
            url = string
        else:
            payload = {'pic': 1, 'enc': encoding, 'word': string}

        self.http = requests.get(url, params=payload)
        self.html = self.http.content.decode(encoding='utf-8')
        self.soup = BeautifulSoup(self.html, 'lxml')

        # Exceptions
        if self.soup.find(class_=CLASS_DISAMBIGUATION):
            raise DisambiguationError(string.decode('utf-8'), self.get_inurls())
        if '百度百科尚未收录词条' in self.html:
            raise PageError(string)
        if self.soup.find(id='vf'):
            raise VerifyError(string)

    def get_info(self):
        """ Get informations of the page """

        info = {}
        title = self.soup.title.get_text()
        info['title'] = title[:title.rfind('_')]
        info['url'] = self.http.url

        try:
            info['page_view'] = self.group.find(id='viewPV').get_text()
            info['last_modify_time'] = self.soup.find(id='lastModifyTime').get_text()
            info['creator'] = self.soup.find(class_=CLASS_CREATOR).get_text()

        finally:
            return info

    def get_content(self):
        """ Get main content of a page """

        content_list = self.soup.find_all(class_=CLASS_CONTENT)
        content = []

        for text in content_list:
            if CLASS_CONTENT[0] in text.get('class'):
                content.append('==== %s ====\n\n' % text.get_text())
            elif CLASS_CONTENT[1] in text.get('class'):
                content.append('\n== %s ==\n' % text.get_text())
            elif CLASS_CONTENT[2] in text.get('class'):
                content.append('\n* %s *\n' % text.get_text())
            elif CLASS_CONTENT[3] in text.get('class'):
                content.append('%s' % text.get_text())

        return '\n'.join(content)

    def get_inurls(self):
        """ Get links inside a page """

        inurls = OrderedDict()
        href = self.soup.find_all(href=re.compile('\/(sub)?view(\/[0-9]*)+.htm'))

        for url in href:
            inurls[url.get_text()] = 'http://baike.baidu.com%s' % url.get('href')

        return inurls

    def get_tags(self):
        """ Get tags of the page """

        tags = []
        for tag in self.soup.find_all(class_=CLASS_TAG):
            tags.append(tag.get_text())

        return tags

    def get_references(self):
        """ Get references of the page """

        references = []

        for ref in self.soup.find_all(class_=CLASS_REFERENCE):
            r = {}
            r['title'] = ref.get_text()
            r['url'] = ref.get('href')
            references.append(r)

        return references


class Search(object):
    def __init__(self, word, results_n=10, page_n=1):
        # Generate searching URL
        url = 'http://baike.baidu.com/search'
        pn = (page_n - 1) * results_n
        payload = {'type': 0, 'submit': 'search', 'pn': pn, 'rn': results_n, 'word': word}

        self.http = requests.get(url, params=payload)
        self.html = self.http.content.decode(encoding='utf-8')
        self.soup = BeautifulSoup(self.html, 'lxml')

    def get_results(self):
        """ Get searching results """

        search_results = []
        items = self.soup.find_all(class_='f')  # get results items

        for item in items:
            result = {}
            a = item.find('a')
            title = a.get_text()  # get result title
            title = title[:title.rfind('_')]
            result['title'] = title
            result['url'] = a.get('href')  # get result links
            # get result discription
            result['discription'] = item.find(class_='abstract').get_text().strip()
            search_results.append(result)

        return search_results


class WordSearch(object):
    def __init__(self):
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/130.0.0.0 Safari/537.36'
        }
        self.pattren = re.compile(r'\[\d+]')

    def get_inurls(self, soup):
        """ Get links inside a page """

        inurls = OrderedDict()
        href = soup.find_all(href=re.compile(r'\/(sub)?view(\/[0-9]*)+.htm'))

        for url in href:
            inurls[url.get_text()] = 'http://baike.baidu.com%s' % url.get('href')

        return inurls

    def _get_baike_page(self, word: str):
        url = 'http://baike.baidu.com/search/word'
        payload = None

        # An url or a word to be Paged
        pattern = re.compile(r'^http:\/\/baike\.baidu\.com\/.*', re.IGNORECASE)
        if re.match(pattern, word):
            url = word
        else:
            payload = {'pic': 1, 'enc': 'utf-8', 'word': word}

        response = requests.get(url, params=payload)
        html = response.content.decode(encoding='utf-8')
        soup = BeautifulSoup(html, 'lxml')

        # Exceptions
        if soup.find(class_=CLASS_DISAMBIGUATION):
            raise DisambiguationError(word, self.get_inurls(soup))
        if '百度百科尚未收录词条' in html:
            raise PageError(word)
        if soup.find(id='vf'):
            raise VerifyError(word)

        info = {}
        title = soup.title.get_text()
        info['title'] = title[:title.rfind('_')]
        info['url'] = response.url

        return info

    def get_summary(self, word: str) -> str:
        """ Get summary of word """
        url_info = self._get_baike_page(word)
        url = url_info.get('url', '')
        if not url:
            return ''
        response = requests.get(url, headers=self.headers)
        html = response.content.decode(encoding='utf-8')
        soup = BeautifulSoup(html, 'lxml')

        summary_tag = soup.find(class_=CLASS_SUMARRY)
        text = summary_tag.get_text()
        text = re.sub(self.pattren, '', text)

        return text


class SearchbySelenium(object):
    def __init__(self):
        self.valid_ip = get_random_proxy()
        self.reset()
        self.pattren = re.compile(r'\s*\[\d+]')

    def reset(self):
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--headless')
        self.options.add_argument('user-agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                  '(KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"')
        self.options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.options.add_experimental_option('useAutomationExtension', False)
        self.options.add_argument('--proxy-server={}'.format(self.valid_ip))

        self.browser = webdriver.Chrome(options=self.options)
        self.browser.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        })

    def close(self):
        self.browser.close()

    def get_search_page_source(self, word: str):
        self.browser.get('https://baike.baidu.com/search')
        wait = WebDriverWait(self.browser, 10)
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'searchInput')))
        input = self.browser.find_element(By.CLASS_NAME, 'searchInput')
        input.send_keys(word)
        input.send_keys(Keys.ENTER)
        wait = WebDriverWait(self.browser, 10)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'total_FTcZY')))
        except Exception as err:
            pass

        return self.browser.page_source

    def get_word_page_source(self, url: str):
        self.browser.get(url)
        wait = WebDriverWait(self.browser, 10)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'lemmaSummary__tEeY J-summary')))
        except Exception as err:
            pass

        return self.browser.page_source

    def parse_page_source(self, page_source) -> Tuple[str, Union[str, list]]:
        soup = BeautifulSoup(page_source, 'lxml')
        title_tag = soup.find(class_='lemmaTitle_qmNnR J-lemma-title')
        title = title_tag.get_text() if title_tag else ''
        summary_tag = soup.find(class_='lemmaSummary__tEeY J-summary')
        if summary_tag:
            text = summary_tag.get_text()
            text = re.sub(self.pattren, '', text)

            synonym_tag = soup.find(class_='tipPanel_XhtKI')
            if synonym_tag:
                synonym_text = synonym_tag.get_text().replace('同义词', '同义词：')
                text = synonym_text + '\n' + text
            return title, text
        else:
            tag_list = soup.find_all('a', class_='title_UaTRY')
            url_list = []
            for tag in tag_list:
                url_list.append({
                    'title': tag.get_text().replace(' - 百度百科', ''),
                    'url': tag['href'] if 'http' in tag['href'] else 'https://baike.baidu.com' + tag['href']
                })
            return title, url_list

    def check_status(self):
        try:
            handle = self.browser.current_window_handle
            return True
        except Exception as err:
            return False

    def get_summary(self, word: str) -> list:
        if not self.check_status():
            self.reset()

        data_list = []
        try:
            page_source = self.get_search_page_source(word)
            _, result = self.parse_page_source(page_source)
            if isinstance(result, list):
                for url_info in result:
                    title, url = url_info['title'], url_info['url']
                    page_source = self.get_word_page_source(url)
                    title, result = self.parse_page_source(page_source)
                    data_list.append({
                        'title': title,
                        'content': result
                    })
            else:
                data_list.append({
                    'title': word,
                    'content': result
                })
        except Exception as err:
            print('Search [{}] error!'.format(word))
            self.valid_ip = get_random_proxy()
        finally:
            self.close()

        return data_list
