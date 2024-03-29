'''

This file contains the class for scrapers. Each scraper should
inherit from this class and overwrite the 'get' function with
a generator.

Scrapers should yield dicts that contain the document (news article,
tweet, blogpost, whatever)

For the following keys, please provide the information specified below:

doctype             : The medium or outlet (e.g. volkskrant, guardian, economist)
url                 : URL from which data is scraped (e.g. volkskrant.nl/artikel1)
publication_date    : Date of publication of article/website as specified by outlet, NOT SCRAPING
text                : Plain (no code/XML or HTML tags) text content

OPTIONAL, BUT RECOMMENDED

_id       : a unique, preferably same as external source identifier of the document (e.g. ISBN, DOI )
language  : If you can safely assume the language of specified documents, please specify them here

'''
import logging
from .document_class import Document
from .database import check_exists, client, elastic_index

logger = logging.getLogger("INCA")

class Scraper(Document):
    '''
    Scrapers are the generic way of adding new documents to the datastore.

    Make scrapers in the 'scrapers' folder by using <datasource>_scraper.py as
    the filename, containing a scraper which inherits from this class.

    the 'get' method should be a self-powered retrieval task, with optional
    arguments.
    '''

    functiontype = 'scraper'
    #language = ''

    def __init__(self):
        Document.__init__(self)

    def get(self):
        ''' This docstring should explain how documents are retrieved

        '''
        logger.warning("You forgot to overwrite the 'get' method of this scraper!")
        yield dict()

    def sideload(self, doc, doctype, language):
        '''
        This function side-loads documents, basically setting scraper doctype, language
        and metadata.

        '''
        doc['doctype']  = self.doctype
        #doc['language'] = self.language)
        doc = self._add_metadata(doc)
        self._verify(doc)
        self._save_document(doc)

    def run(self, save=True, check_if_url_exists=False, *args, **kwargs):
        
        '''
        DO NOT OVERWRITE THIS METHOD

        This is an internal function that calls the 'get' method and saves the
        resulting documents.
        '''

        logger.info("Started scraping")
        if save == True:
            for doc in self.get(save, *args, **kwargs):
                if check_if_url_exists == False or client.search(index=elastic_index, body={
                    'query': {'term': {'url': doc['url']}}})['hits']['total'] == 0:
                    if type(doc)==dict:
                        doc = self._add_metadata(doc)
                        self._save_document(doc)
                    else:
                        doc = self._add_metadata(doc)
                        self._save_documents(doc)
                else:
                    logger.info('A document with this URL already existed - did not save the new one.')
        else:
            return [self._add_metadata(doc) for doc in self.get(save, *args, **kwargs)]

        logger.info('Done scraping')

    def _test_function(self):
        '''tests whether a scraper works by seeing if it returns at least one document

           GENERALLY DON'T OVERWRITE THIS METHOD!
        '''
        try:
            self.check_exists = lambda x: False # overwrite check exists to ensure start conditions
            for doc in self.get():
                logger.info("{self.__class__} works!".format(**locals()))
                return {"{self.__class__}".format(**locals()) :True}
        except:
            return {"{self.__class__}".format(**locals()) : False}

    def _check_exists(self, *args, **kwargs):
        return check_exists(*args, **kwargs)

class UnparsableException(Exception):
    def __init__(self):
        logger.warn('Could not parse the content; maybe the string does not contain valid HTML?')
