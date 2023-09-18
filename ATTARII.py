from config import parse_args
from dataextractiontools import amazon_tabular_info_scraper, amazon_textual_info_scraper


def main():
    """
    Main function for scraping textual and tabular information from an Amazon product page.
    This function parses command-line arguments, determines the type of information to extract (tabular or textual),
    and initiates the appropriate scraping process based on the provided URL and arguments.
    """

    args = parse_args()

    if args.info_type == "tabular":
        tabular_info_extraction = amazon_tabular_info_scraper.AmazonTabularInfoExtraction(args)
        tabular_info_extraction.extract(args.URL)

    if args.info_type == "textual":
        textual_info_extraction = amazon_textual_info_scraper.AmazonTextualInfoExtraction(args)
        textual_info_extraction.extract(args.URL)


if __name__ == "__main__":
    main()