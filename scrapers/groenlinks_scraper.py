import requests
import datetime
from lxml.html import fromstring
from core.scraper_class import Scraper
from scrapers.rss_scraper import rss
from core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger(__name__)

class groenlinks(Scraper):
    """Scrapes Groenlinks"""

    def __init__(self,database=True, maxpages = 2):
        '''
        maxpage: number of pages to scrape
        '''
        
        self.database = database
        self.START_URL = "https://www.groenlinks.nl/nieuws"
        self.BASE_URL = "https://www.groenlinks.nl"
        self.MAXPAGES = maxpages

    def get(self):
        '''                                                                     
        Fetches articles from Groenlinks
        '''
        self.doctype = "Groenlinks (pol)"
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=9, day=29)


        releases = []

        page = 0
        current_url = self.START_URL+str(page)
        overview_page = requests.get(current_url, timeout = 10)
        first_page_text=""
        while overview_page.text!=first_page_text:
            logger.debug("How fetching overview page {}".format(page))
            if page > self.MAXPAGES:
                break
            elif page ==1:
                first_page_text=overview_page.text             
            tree = fromstring(overview_page.text)
            linkobjects = tree.xpath('//*[@class="read-more"]')
            links = [self.BASE_URL+l.attrib['href'] for l in linkobjects if 'href' in l.attrib]
            for link in links:
                logger.debug('ik ga nu {} ophalen'.format(link))
                try:
                    current_page = requests.get(link, timeout = 10)
                except requests.ConnectionError as e:
                    try:
                        link = link[25:]
                        current_page = requests.get(link, timeout = 10)
                    except:
                        print("Connection Error!")
                        print(str(e))
                tree = fromstring(current_page.text)
                try:
                    title= " ".join(tree.xpath('//*[@id = "page-title"]/text()'))
                except:
                    logger.debug("no title")
                    title = ""
                try:
                    publication_date = "".join(tree.xpath('//*[@class = "submitted-date"]/text()'))
                    MAAND2INT = {"januari":1, "februari":2, "maart":3, "april":4, "mei":5, "juni":6, "juli":7, "augustus":8, "september":9, "oktober":10, "november":11, "december":12}
                    dag = publication_date[:2]
                    jaar= publication_date[-4:]
                    maand= publication_date[2:-4].strip().lower()
                    publication_date = datetime.datetime(int(jaar), int(MAAND2INT[maand]),int(dag))
                    publication_date = publication_date.date()
                except:
                    publication_date = ""
                try:
                    teaser=" ".join(tree.xpath('//*[@class = "intro"]/p/text()')).strip()
                except:
                    logger.debug("no teaser")
                    teaser = ""
                try:
                    text = " ".join(tree.xpath('//*[@class = "content-wrapper"]/p/text()')).strip()
                except:
                    logger.info("no text?")
                    text = ""
                text = "".join(text)
                try:
                    quote = " ".join(tree.xpath('//*[@class = "content-wrapper"]/blockquote/p/text()')).strip()
                except:
                    quote = ""
                quote = "".join(quote)
                releases.append({'text':text,
                                 'teaser': teaser,
                                 'title':title,
                                 'quote':quote,
                                 'url':link,
                                 'publication_date':publication_date})
        
            page+=1
            current_url = self.START_URL+'?page'+str(page)
            overview_page=requests.get(current_url, timeout = 10)

        return releases