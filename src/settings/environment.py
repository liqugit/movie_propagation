"""
File: environment.py
Author: Joao Moreira
Creation Date: May 28, 2015

Description:
Environment file for the IMDb Gender differences project.
Contains the database connection information.
"""
try:
    from . import config
except ImportError:
    # dummy object if config.py doesn't exist
    config = object()
    # Settings attributes pulled out of config module:
    #  - MONGO_HOST
    #  - MONGO_PORT
    #  - MONGO_DB
    #  - MONGO_USER
    #  - MONGO_PASS
    #  - MONGO_AUTH

mongodb_settings = {
    "host": getattr(config, "MONGO_HOST", "localhost"),
    "port": getattr(config, "MONGO_PORT", "27017"),
    "db": getattr(config, "MONGO_DB", "test"),
    "user": getattr(config, "MONGO_USER", "mongo"),
    "password": getattr(config, "MONGO_PASS", ""),
    "mechanism": getattr(config, "MONGO_AUTH", "MONGODB-CR")
}

# Contains movie information of name, date, and id.
movies_settings = mongodb_settings.copy()
movies_settings["collection"] = "movies"
movies_settings["indexes"] = [
    [[("year", 1)], {}],
]

# Contains actor information including name, gender, and id.
actor_settings = mongodb_settings.copy()
actor_settings["collection"] = "actor"
actor_settings["indexes"] = [
    [[("movies_list", 1)], {}],
]

# Contains director information including name, gender, and id.
director_settings = mongodb_settings.copy()
director_settings["collection"] = "director"

# Contains director information including name, gender, and id.
producer_settings = mongodb_settings.copy()
producer_settings["collection"] = "producer"
