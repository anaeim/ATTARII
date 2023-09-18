from config import parse_args
from dataextractiontools import amazon_tabular_info_scraper, amazon_textual_info_scraper


def main():
    args = parse_args()

    if args.info_type == "tabular":
        tabular_info_extraction = amazon_tabular_info_scraper.AmazonTabularInfoExtraction(args)
        tabular_info_extraction.extract(args.URL)



if __name__ == "__main__":
    main()