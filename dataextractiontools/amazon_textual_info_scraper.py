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

    def extract_bullet_points(self):
        try:
            _list = []  # save each bullet point as an item of _list
            for item in self.soup_obj.select('#feature-bullets li'):
                item = item.select('.a-list-item')[0].get_text().strip()

                # to remove template instructions, e.g. "Make sure this fits by entering your model number.", from the extracted bullet points.
                if item == "Make sure this fits by entering your model number.":
                    continue

                # to remove remove_unicode_chars
                item = utils.remove_unicode_chars(item)

                _list.append(item)

        except:
            _list = ['']

        self.product_textual_info_dict['bullet_points'] = _list

    def extract_product_description(self):
        """extracts the product description from the Amazon product web page
        """

        try:
            # variant 1
            descriptions = self.soup_obj.select('#productDescription p')
            _product_descriptions_list = []
            for description in descriptions:
                description = description.get_text().strip()
                _product_descriptions_list.append(description)
                _product_descriptions = ' '.join(_product_descriptions_list)

            # variant 2
            if len(_product_descriptions_list) == 0:
                descriptions = self.soup_obj.select('#productDescription_feature_div p')
                _product_descriptions_list = []
                for description in descriptions:
                    description = description.get_text().strip()

                    _product_descriptions_list.append(description)
                    _product_descriptions = ' '.join(_product_descriptions_list)

            if len(_product_descriptions_list) == 0:
                    _product_descriptions = ""

        except:
            _product_descriptions = ""

        _product_descriptions = utils.remove_unicode_chars(_product_descriptions)

        self.product_textual_info_dict['product_description'] = _product_descriptions