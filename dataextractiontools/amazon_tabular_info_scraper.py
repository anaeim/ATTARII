import re
import json
import sys
from pathlib import Path

from bs4 import BeautifulSoup
from selenium import webdriver

from dataextractiontools.utils import remove_unicode_chars


class AmazonTabularInfoExtraction():
    """A class used to download Amazon e-commerce product web pages using the URL and extract the tabular data included in the Amazon web page

    ...

    Attributes
    ----------
    URL : str
        the url of the product web page
    soup_obj : BeautifulSoup
        An instance of BeautifulSoup using the page_content
    product_detail_table_dict : dict
        A dictionary containing the product detail tables extracted from the Amazon product web page
    product_overview_table_dict : dict
        A dictionary containing the product overview tables extracted from the Amazon product web page
    product_detail_table_write_path : str
        the path of json file in which the product detail tables are written (default ./extracted_info/product_detail_table.json)
    product_overview_table_write_path : str
        the path of json file in which the product overview tables are written (default ./extracted_info/product_overview_table.json)

    Methods
    -------
    dl_page()
        downloads the product web pages and create a BeautifulSoup object
    get_product_overview_table()
        extracts the product overview tables from the Amazon product web page
    get_product_detail_table_all_types()
        extracts all types of product detail tables from the Amazon product web page
    get_product_detail_table_type1()
        extracts type1 of product detail tables from the Amazon product web page
    get_product_details_table_type2()
        extracts type2 of product detail tables from the Amazon product web page
    get_product_details_table_type3()
        extracts type3 of product detail tables from the Amazon product web page
    print_dict_indented(dict_)
        prints a dictionary in an indented format
    create_empty_info_dict(path)
        creates a empty json file in which our extracted tables are written in dictionary format
    dump_info_dict_to_json(self, info_dict, path)
        dumps the extracted info_dict into an already generated json file
    __call__()
        call the instance like a function and calls the class methods in the defined order
    """

    def __init__(self, URL):
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
        self.product_detail_table_dict = dict()
        self.product_overview_table_dict = dict()

        path = Path()
        self.product_detail_table_write_path = path.cwd() / self.dump_info_path / 'product_detail_table.json'
        self.product_overview_table_write_path = path.cwd() / self.dump_info_path / 'product_overview_table.json'

    def dl_page(self):
        """downloads the product web pages and create a BeautifulSoup object
        """

        driver = webdriver.Firefox()
        driver.get(self.URL)
        self.page_source = driver.page_source
        self.soup_obj = BeautifulSoup(self.page_source,"lxml")
        driver.close()


    # def extract_title(self):
    #     try:
    #         self.dl_page()
    #         title_string = self.soup_obj.select('div#title_feature_div')[0].getText().strip()
    #         title_string = remove_unicode_chars(title_string)

    #     except:
    #         title_string = "NOT FOUND"	

    #     return title_string


    def get_product_overview_table(self):
        """extracts the product overview tables from the Amazon product web page
        """

        try:	
            _product_overview_table = {}
            my_keys = []
            my_values = []
            count = 0

            for item in self.soup_obj.select('div#productOverview_feature_div tr td'):
                item = item.get_text().strip()
                if count%2 == 0: my_keys.append(item)
                if count%2 == 1: my_values.append(item)
                count += 1

            _product_overview_table = {my_keys[i]:my_values[i] for i in range(len(my_keys))}
        
        except:
            _product_overview_table = {}

        self.product_overview_table_dict = _product_overview_table


    def get_product_detail_table_all_types(self):
        """extracts all types of product detail tables from the Amazon product web page
        """

        # type1:
        if len(self.get_product_detail_table_type1()) > 0:
            _product_detail_table = self.get_product_detail_table_type1()

        # type2
        elif len(self.get_product_details_table_type2()) > 0:
            _product_detail_table = self.get_product_details_table_type2()

        # type3
        elif len(self.get_product_detail_table_type3()) > 0:
            _product_detail_table = self.get_product_detail_table_type3()

        # when there is any kind of product detail table
        else:
            _product_detail_table = {'NA':'NA'}

        self.product_detail_table_dict = _product_detail_table


    def get_product_detail_table_type1(self):
        """extracts type1 of product detail tables from the Amazon product web page

        Returns
        -------
        dict
            product detail table type1
        """

        my_keys = [] # with th tags
        my_values = [] # with td tags

        for item in self.soup_obj.select('div#prodDetails tr th'):
            item = item.get_text().strip()
            item = remove_unicode_chars(item)
            my_keys.append(item)

        for item in self.soup_obj.select('div#prodDetails tr td'):
            item = item.get_text().strip()
            item = remove_unicode_chars(item)
            my_values.append(item)

        _product_detail_table = {my_keys[i]:my_values[i] for i in range(len(my_keys))}

        # if there is a 'Best Sellers Rank' attribute, it processes the attribute and returns the value as a list of ranks
        if 'Best Sellers Rank' in _product_detail_table.keys():
            Best_Sellers_Rank = [] # Best_Sellers_Rank attributes
            subitem = _product_detail_table['Best Sellers Rank']
            subitem = subitem.split("#")[1:]

            for sub_subitem in subitem:
                sub_subitem = re.sub('\(See .*\)','', sub_subitem).strip()
                Best_Sellers_Rank.append("#" + sub_subitem)
            
            _product_detail_table['Best Sellers Rank'] = Best_Sellers_Rank

        return _product_detail_table


    def get_product_details_table_type2(self):
        """extracts type2 of product detail tables from the Amazon product web page

        Returns
        -------
        dict
            product detail table type2
        """

        _product_detail_table = {}
        for item in self.soup_obj.select('#detailBullets_feature_div li'):
            item = item.select('.a-list-item')[0].get_text().strip()
            item = item.split(':')

            if len(item) > 1:
                my_key = item[0].replace('\n                                    \u200f\n                                        ', '').strip()
                my_value = item[1].replace('\n                                    \u200e\n                                 ', '').strip()
                _product_detail_table[my_key] = my_value

        check_Best_Sellers_Rank = False 
        Best_Sellers_Rank = [] # Best_Sellers_Rank attributes

        for item in self.soup_obj.select('.a-unordered-list.a-nostyle.a-vertical.a-spacing-none.detail-bullet-list li'):
            item = item.get_text().strip()
            item = item.split(':')

            if 'Best Sellers Rank' in item: # checks if there is a Best_Sellers_Rank attribute in the items
                check_Best_Sellers_Rank = True

                for subitem in item:
                    if "#" in subitem: # only if a subitem has "#" character
                        subitem = subitem.split("#")[1:]
                        for sub_subitem in subitem:
                            sub_subitem = re.sub('\(See .*\)','', sub_subitem).strip()
                            # print(sub_subitem)
                            Best_Sellers_Rank.append("#" + sub_subitem)
        
        if check_Best_Sellers_Rank:
            _product_detail_table['Best_Sellers_Rank'] = Best_Sellers_Rank

        return _product_detail_table


    def get_product_detail_table_type3(self):
        """extracts type3 of product detail tables from the Amazon product web page

        Returns
        -------
        dict
            product detail table type3
        """

        _product_detail_table = {}
        my_keys = []
        my_values = []
        count = 0

        for item in self.soup_obj.select('div#tech.content-grid-alternate-styles.mako-v2 tr td'):
            item = item.get_text().strip()
            if count%2 == 0: my_keys.append(item)
            if count%2 == 1: my_values.append(item)
            count += 1

        _product_detail_table = {my_keys[i]:my_values[i] for i in range(len(my_keys))}

        return _product_detail_table


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
        path : str
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
        path : str
            the path of a json file in which our extracted tables are written
        """

        print(f'dumped in {path}.')
        with open(path, 'r+') as fh:
            json.dump(info_dict, fh, indent=4)


    def __call__(self):
        """call the instance like a function and calls the class methods in the defined order
        """
        self.dl_page()
        print('product_detail_table:')
        self.get_product_detail_table_all_types()
        self.print_dict_indented(self.product_detail_table_dict)
        self.create_empty_info_dict(self.product_detail_table_write_path)
        self.dump_info_dict_to_json(self.product_detail_table_dict, self.product_detail_table_write_path)

        print('\n\n\nproduct_overview_table:')
        self.get_product_overview_table()
        self.print_dict_indented(self.product_overview_table_dict)
        self.create_empty_info_dict(self.product_overview_table_write_path)
        self.dump_info_dict_to_json(self.product_overview_table_dict, self.product_overview_table_write_path)



URL = "https://www.amazon.com/New-Apple-Watch-GPS-40mm/dp/B08KHR6B3W/ref=sr_1_2?keywords=apple+watch&qid=1668543539&sr=8-2"
amazon_scrapor = AmazonTabularContentScraper(URL=URL)
amazon_scrapor()
# print(amazon_scrapor.product_detail_table_dict)
# print(amazon_scrapor.product_overview_table_dict)