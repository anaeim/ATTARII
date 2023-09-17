import re
import os
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver

from dataextractiontools import utils


class AmazonTextualInfoExtraction():
    """A class used to download Amazon e-commerce product web pages using the URL and extract the tabular data included in the Amazon web page

    ...

    Attributes
    ----------
    URL : str
        the URL of the product web page
    args : namedtuple
        the arguments pre-defined by the user and imported from config.py
    verbosity_enabled : bool
        display the extracted tabular info
    dump_info_enabled : bool
        dump the extracted info as a json file
    dump_info_path : str
        the directory to dump the extracted info
    soup_obj : BeautifulSoup
        an instance of BeautifulSoup using the page_content
    product_textual_info_dict : dict
        a dictionary containing the product textual information extracted from the Amazon product web page
    product_textual_info_write_path : os.PathLike
        the path of json file in which the product_textual_info_dict is written


    Methods
    -------
    dl_page()
        downloads the product web pages and create a BeautifulSoup object
    extract_title()
        extracts the product title from the Amazon product web page
    extract_bullet_points()
        extracts the bullet points from the Amazon product web page
    extract_product_description()
        extracts the product description from the Amazon product web page
    extract(URL)
        extracts the textual information from a Amazon product webpage using the URL of the page
    """

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
        """downloads the product web pages and create a BeautifulSoup object
        """

        driver = webdriver.Firefox()
        driver.get(self.URL)
        self.page_source = driver.page_source
        self.soup_obj = BeautifulSoup(self.page_source,"lxml")
        driver.close()

    def extract_title(self):
        """extracts the product title from the Amazon product web page
        """

        try:
            _title = self.soup_obj.select('div#title_feature_div')[0].getText().strip()
            _title = utils.remove_unicode_chars(_title)

        except:
            _title = ''

        self.product_textual_info_dict['title'] = _title

    def extract_bullet_points(self):
        """extracts the bullet points from the Amazon product web page
        """

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

    @staticmethod
    def print_dict_indented(dict_):
        """prints a dictionary in an indented format

        Parameters
        ----------
        dict_ : dict
            a dictionary of tabular data extracted from the Amazon product web page
        """

        print(json.dumps(dict_, indent=4))

    @staticmethod
    def create_empty_info_dict(path):
        """creates a empty json file in which our extracted tables are written in dictionary format
        
        Parameters
        ----------
        path : os.PathLike
            the path of a json file in which our extracted tables are written
        """

        dict_temp = dict()
        with path.open('w') as fh:
            json.dump(dict_temp, fh, indent=4)

    def dump_info_dict_to_json(self, info_dict, path):
        """dumps the extracted info_dict into an already generated json file

        Parameters
        ----------
        info_dict : dict
            tabular data extracted from the Amazon product web page in a dictionary format
        path : os.PathLike
            the path of a json file in which our extracted tables are written
        """

        print(f'dumped in {path}.')
        with path.open('r+') as fh:
            json.dump(info_dict, fh, indent=4)

    def extract(self, URL):
        """extracts the textual information from a Amazon product webpage using the URL of the page

        Parameters
        ----------
        URL : str
            the URL of a Amazon product web page
        """

        self.URL = URL
        self.dl_page()

        self.extract_title()
        self.extract_bullet_points()
        self.extract_product_description()

        if self.verbosity_enabled:
            print('product_detail_table:')
            self.print_dict_indented(self.product_textual_info_dict)

        if self.dump_info_enabled:
            self.create_empty_info_dict(self.product_textual_info_write_path)
            self.dump_info_dict_to_json(self.product_textual_info_dict, self.product_textual_info_write_path)