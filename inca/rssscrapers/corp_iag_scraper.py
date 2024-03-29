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

class iag(rss):
    """Scrapes IAG"""

    def __init__(self):
        self.doctype = "iag (corp)"
        self.rss_url ='http://www.iairgroup.com/corporate.rss?c=240949&Rule=Cat=news~subcat=ALL'
        self.version = ".1"
        self.date = datetime.datetime(year=2017, month=6, day=28)


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
        text    the plain text of the article                                                                                                                                                                                                                              
        '''
        
        tree = fromstring(htmlsource)
        try:
            title="".join(tree.xpath('//*/span[@class="ccbnTtl"]//text()')).strip()
        except:
            title= ""
            logger.warning("Could not parse article title")
        try:
            text="".join(tree.xpath('//*[@class="cb"]//text() | //*[@class="ca"]//text() | //*[@class="cg"]//text() | //*[@class="cc"]//text()')).strip()
        except:
            logger.warning("Could not parse article text")
            text = ""
        text = "".join(text)
        releases={"title":title.strip(),
                  "text":polish(text).strip()
                  }

        return releases
