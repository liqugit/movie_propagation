"""
File: imdb_parse.py
Author: Joao Moreira
Creation Date: Oct 3, 2016

Description:
Extends ArgumentParser to use specific command line arguments for this project.
"""
import argparse

def positive_int(value):
    i_value = int(value)
    if i_value < 0:
        raise argparse.ArgumentTypeError(
            "{} is not a positive integer".format(value)
        )
    return i_value


class ImdbArgumentParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(ImdbArgumentParser, self).__init__(*args, **kwargs)

        self.add_argument(
            "-p", "--page", dest="page", type=positive_int, default=0,
            help="Mongo results page to process"
        )
        self.add_argument(
            "-s", "--size", dest="size", type=positive_int, default=0,
            help="Size of page of Mongo results"
        )
        self.add_argument(
            "-e", "--element", dest="element", default="actor",
            choices={"actor", "director", "producer", "movies"},
            help="Type of element to analyze"
        )
