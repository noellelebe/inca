import requests
import datetime
from lxml.html import fromstring
from inca.core.scraper_class import Scraper
from inca.scrapers.rss_scraper import rss
from inca.core.database import check_exists
import feedparser
import re
import logging

logger = logging.getLogger("INCA")

def polish(textstring):
    #This function polishes the full text of the articles - it separated the lead from the rest by ||| and separates paragraphs and subtitles by ||.
    lines = textstring.strip().split('\n')
    lead = lines[0].strip()
    rest = '||'.join( [l.strip() for l in lines[1:] if l.strip()] )
    if rest: result = lead + ' ||| ' + rest
    else: result = lead
    return result.strip()

class gemalto (rss):
    """Scrapes Gemalto"""

    def __init__(self):
        self.doctype = "gemalto (corp)"
        self.rss_url ='http://www.gemalto.com/_layouts/15/feed.aspx?xsl=1&web=/press/rss&page=ccdbcfc3-cf39-419e-ad30-ff414b97b068&wp=9cc71aca-9378-474a-98a2-99673b290d2b'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=21)


    def parsehtml(self,htmlsource):
        '''                                                                                                                                                                                                                                                                
        Parses the html source to retrieve info that is not in the RSS-keys                                                                                                                                                                                                 
        
        Parameters                                                                                                                                                                                                                                                         
        ----                                                                                                                                                                                                                                                              
        htmlsource: string                                                                                                                                                                                                                                                 
            html retrived from RSS feed                                                                                                                                                                                                                                     

        yields                                                                                                                                                                                                                                                            
        ----                                                                                                                                                                                                                                                               
        title    the title of the article                                                                                                                                                                                                                                 
        teaser    the intro to the artcile                                                                                                                                                                                                                                 
        text    the plain text of the article                                                                                                                                                                                                                               
        '''

        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*[@class="sub-content"]/h1/text()')).strip()
        except:
            logger.warning("Could not parse article title")
            title = ""
        try:
            text="".join(tree.xpath('//*[@class="ms-rtestate-field"]//text() | //*[@class="articleBody"]/p//text()')).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        text = "".join(text)
        extractedinfo={"title":title.strip(),
                       "text":polish(text).strip()
                       }

        return extractedinfo
