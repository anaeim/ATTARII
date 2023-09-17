import re
import os
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver

from dataextractiontools import utils


class AmazonTextualInfoExtraction():
    def __init__(self, args):
        """
        Parameters
        ----------
        args : namedtuple
            the namespace variable that contains the config for the scraper
        """

        self.verbosity_enabled = args.verbosity_enabled
        self.dump_info_enabled = args.dump_info_enabled
        self.dump_info_path = args.dump_info_path

        self.URL = None
        self.soup_obj = None
        self.product_textual_info_dict = dict()

        path = Path()
        self.product_textual_info_write_path = path.cwd() / self.dump_info_path / 'product_textual_info.json'

    def dl_page(self):
        driver = webdriver.Firefox()
        driver.get(self.URL)
        self.page_source = driver.page_source
        self.soup_obj = BeautifulSoup(self.page_source,"lxml")
        driver.close()

    def extract_title(self):
        try:
            _title = self.soup_obj.select('div#title_feature_div')[0].getText().strip()
            _title = utils.remove_unicode_chars(_title)

        except:
            _title = ''

        self.product_textual_info_dict['title'] = _title