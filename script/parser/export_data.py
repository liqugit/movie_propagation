"""
File: export_data.py
Author: Joao Moreira
Creation Date: Apr 7, 2017

Description:
Export all relevant data for the manuscript to a series of json files.
"""
import json
import os
import sys

sys.path[0] = os.path.abspath(os.path.join(os.pardir, os.pardir, "src"))
from common.database import MongoConnection
from settings.environment import (
    actor_settings, director_settings, movies_settings, producer_settings
)

# raw data location accessible to the manuscript code
MANUSCRIPT_RAW_DATA = os.path.abspath(os.path.join(
    os.pardir, os.pardir, "data", "raw_data"
))

def export_movies():
    """
    Exports data from the movies collection to json.
    """
    movie_coll = MongoConnection(movies_settings).collection

    movie_cursor = movie_coll.find(
        {},
        {
            "adjusted_budget": 1, "all_actors": 1, "director": 1, "producer": 1,
            "gender_percent": 1, "genre": 1, "year": 1, "title": 1
        }
    )
    all_movies = list(movie_cursor)

    movies_fpath = os.path.join(MANUSCRIPT_RAW_DATA, "movies.json")
    with open(movies_fpath, "w") as fobj:
        json.dump(all_movies, fobj)


def export_actors():
    """
    Exports data from the actors collection to json.
    """
    actor_coll = MongoConnection(actor_settings).collection

    actor_cursor = actor_coll.find(
        {},
        {"name": 1, "gender": 1, "movies_list": 1}
    )
    all_actors = list(actor_cursor)

    actors_fpath = os.path.join(MANUSCRIPT_RAW_DATA, "actors.json")
    
    for actor in all_actors:
        if type(actor) != dict:
            print(actor)
    with open(actors_fpath, "w") as fobj:
        json.dump(all_actors, fobj)


def export_directors():
    """
    Exports data from the directors collection to json.
    """
    dir_coll = MongoConnection(director_settings).collection

    dir_cursor = dir_coll.find(
        {"movies_list.type": "director"},
        {"death_date": 0, "birth_date": 0}
    )
    all_dirs = list(dir_cursor)

    dirs_fpath = os.path.join(MANUSCRIPT_RAW_DATA, "directors.json")
    with open(dirs_fpath, "w") as fobj:
        json.dump(all_dirs, fobj)


def export_producers():
    """
    Exports data from the producers collection to json.
    """
    prod_coll = MongoConnection(producer_settings).collection

    prod_cursor = prod_coll.find()
    all_prods = list(prod_cursor)

    prods_fpath = os.path.join(MANUSCRIPT_RAW_DATA, "producers.json")
    with open(prods_fpath, "w") as fobj:
        json.dump(all_prods, fobj)


def main():

    # The raw data directory is not in the repo so we need to create it first.
    if not os.path.exists(MANUSCRIPT_RAW_DATA):
        os.makedirs(MANUSCRIPT_RAW_DATA)

    # print('Export movies')
    # export_movies()
    # print('Export actors')
    # export_actors()
    # print('Export directors')
    # export_directors()
    print('Export producers')
    export_producers()

    return 0


if __name__ == '__main__':
    sys.exit(main())
