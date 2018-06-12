__author__ = "Amaral LAN"
__copyright__ = "Copyright 2018, Amaral LAN"
__credits__ = ["Amaral LAN"]
__version__ = "1.0"
__maintainer__ = "Amaral LAN"
__email__ = "amaral@northwestern.edu"
__status__ = "Production"

import pymongo
import json
from copy import deepcopy
import sys
import os

src_dir = os.path.abspath(os.path.join(os.pardir, 'src'))
sys.path[0] = src_dir
from support import ROLES, CREDITS
from my_mongo_db_login import DB_LOGIN_INFO


def update_career(year, career_summary):
    career_summary['number'] += 1
    if year < career_summary['first']:
        career_summary['first'] = year
    if year > career_summary['last']:
        career_summary['last'] = year

    return career_summary


if __name__ == "__main__":
    # Access  database and collections
    connection = pymongo.MongoClient(DB_LOGIN_INFO['credentials'], DB_LOGIN_INFO['port'])
    db = connection['imdb_gender']
    final_movies = db['final_movies']
    final_persons = db['final_persons']
    print('Opened connection')

    persons = {}
    for person in final_persons.find({}):
        persons[person['_id']] = person
    print('\nLoaded {:d} persons'.format(len(persons)))

    # Create list of dictionaries with summary of industry participants careers
    #
    career_summary = {}
    for person_id in persons:
        career_summary[person_id] = {}
        for creds in ['producing', 'directing']:
            career_summary[person_id][creds] = {'first': 3010, 'last': 1700, 'number': 0}
        career_summary[person_id]['acting_all'] = {'first': 3010, 'last': 1700, 'number': 0}
        career_summary[person_id]['acting_credited'] = {'first': 3010, 'last': 1700, 'number': 0}


    # Get list of dictionaries with movies for analysis
    #
    # if ('Short' not in movie['genres'] or int(movie['year']) < 1930) and 'Animation' not in movie['genres']:
    #     if movie['is_usa'] and ('is_tv:' not in movie.keys() or not movie['is_tv:']):
    #
    #
    movies = []
    for movie in final_movies.find():
        if 'year' in movie.keys() and str(movie['year']).isdigit():
            if 'AFI match' in movie.keys() and movie['AFI match'] != False and 'Animation' not in movie['genres']:
                if int(movie['year']) >= 1910 and int(movie['year']) <= 2010:
                    if len(movie['cast_all']) > 0 and (len(movie['directors']) > 0 or len(movie['producers']) > 0):
                        tmp = {}
                        for key in ['_id', 'year', 'title', 'genres', 'producers', 'directors', 'cinematographers',
                                    'screenwriters', 'casting_directors', 'cast_all', 'cast_credited', 'AFI match']:
                            if key in movie.keys():
                                tmp[key] = deepcopy(movie[key])
                        if 'revenue' in movie.keys():
                            if 'adjusted_budget' in movie['revenue'].keys():
                                tmp['adjusted_budget'] = deepcopy(movie['revenue']['adjusted_budget'])

                        movies.append(tmp)
    print('\n\nLoaded {:d} movies'.format(len(movies)))


    # Update career summary of industry participants and female percentage in movies
    #
    for i, movie in enumerate(movies):
        #     print(i, movie['title'])
        year = int(movie['year'])
        for k in range(len(ROLES)):
            cred = ROLES[k]
            cred_type = CREDITS[k] + '_gender_percentage'
            if len(movie[cred]) == 0:
                movie[cred_type] = None
            else:
                count_female = 0
                count_total = 0
                for item in movie[cred]:
                    if 'cast_all' == cred:
                        person_id = item
                        career_summary[person_id]['acting_all'] = update_career(year,
                                                                                career_summary[person_id]['acting_all'])
                    elif 'cast_credited' == cred:
                        person_id = item
                        career_summary[person_id]['acting_credited'] = update_career(year,
                                                                                     career_summary[person_id][
                                                                                         'acting_credited'])
                    elif 'directors' == cred:
                        person_id = item[0]
                        career_summary[person_id]['directing'] = update_career(year,
                                                                               career_summary[person_id]['directing'])
                    elif 'producers' == cred:
                        person_id = item[0]
                        career_summary[person_id]['producing'] = update_career(year,
                                                                               career_summary[person_id]['producing'])
                    else:
                        person_id = item[0]

                    count_total += 1
                    if persons[person_id]['gender'] == 'female':
                        count_female += 1

                movie[cred_type] = 100 * count_female / count_total

    print('\n', person_id, career_summary[person_id], '\n')

    file_path = './movies.json'
    with open(file_path, 'w') as file_out:
            json.dump(movies, file_out)

    people = []
    for person_id in career_summary.keys():
        tmp = {'_id': person_id}
        tmp.update( career_summary[person_id] )
        people.append( tmp )

    print(people[-1])

    file_path = './career.json'
    with open(file_path, 'w') as file_out:
            json.dump(people, file_out)


