import argparse
from pathlib import Path

def parse_args():
    parser = argparse.ArgumentParser()
    add_arg = parser.add_argument

    add_arg("--URL", default="https://www.amazon.com/dp/B08KHR6B3W/", help="the URL of Amazon product webpage", type=str)
    add_arg("--info-type", default="tabular", choices=["tabular","textual"], help="specify the type of information for ATARI", type=str)
    add_arg("--verbose", action="store_true", help="display the extracted info")
    add_arg("--dump-info", action="store_true", help="dump the extracted info as a json file")
    add_arg("--dump-info-path", help="take the directory to dump the extracted info", default="./extracted_info", type=str)

    return parser.parse_args()

if __name__ == "__main__":
    print(parse_args())
