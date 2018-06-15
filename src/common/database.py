"""
File: database.py
Author: Joao Moreira and Adam Pah
Creation Date: Jan 13, 2015

Description:
Contains a custom MongoClient class with all the functions needed to connect to
a Mongo database.
"""
import sys
import random

from pymongo import MongoClient
from bson.objectid import ObjectId
import bson

class MongoConnection(object):
    """
    Handle the mongo connections
    """
    auth_mechanisms = {"MONGODB-CR", "SCRAM-SHA-1"}

    def __init__(self, cxnSettings, **kwargs):
        self.settings = cxnSettings
        self.mongoURI = self._constructURI()
        self.connect(**kwargs)
        self.ensure_index()

    def _constructURI(self):
        """
        Construct the mongo URI
        """
        mongoURI = "mongodb://"

        # User/password handling
        if "user"in self.settings and "password" in self.settings:
            mongoURI += self.settings["user"] + ":" + self.settings["password"]
            mongoURI += "@"
        elif "user" in self.settings:
            print("Missing password for given user, proceeding without either")
        elif "password" in self.settings:
            print("Missing user for given passord, proceeding without either")

        # Host and port
        try:
            mongoURI += self.settings["host"] + ":"
        except KeyError:
            print("Missing the hostname. Cannot connect without host")
            raise
        try:
            mongoURI += str(self.settings["port"])
        except KeyError:
            print("Missing the port. Substituting default port of 27017")
            mongoURI += "27017"

        # Authentication mechanism
        if "mechanism" in self.settings:
            if self.settings["mechanism"] not in MongoConnection.auth_mechanisms:
                msg = "Invalid authorization mechanism. Must be one of: "
                msg += ", ".join(MongoConnection.auth_mechanisms)
                raise ValueError(msg)
            mongoURI += "/?authMechanism=" + self.settings["mechanism"]

        return mongoURI

    def _formatId(self, bid):
        """
        Checks an Id to see if it is in ObjectId type.
        If not, returns as ObjectId type
        input:
            bson_id
        output:
            bson_id (ObjectId)
        """
        # Check the type
        if isinstance(bid, bson.objectid.ObjectId):
            bid = ObjectId(bid)
        return bid

    def connect(self, **kwargs):
        """
        Establish the connection, database, and collection
        """
        self.connection = MongoClient(self.mongoURI, **kwargs)

        try:
            self.db = self.connection[self.settings["db"]]
        except KeyError:
            print("Must specify a database as a 'db' key in the settings file")
            sys.exit()

        try:
            self.collection = self.db[self.settings["collection"]]
        except KeyError:
            print("Should have a collection.", end=" ")
            print("Starting a collection in database for current connection as test")
            self.collection = self.db["test"]

    def ensure_index(self):
        """
        Ensures the connection has all given indexes.
        indexes: list of (`key`, `direction`) pairs.
            See docs.mongodb.org/manual/core/indexes/ for possible `direction`
            values.
        """
        if "indexes" in self.settings:
            for index in self.settings["indexes"]:
                self.collection.ensure_index(index[0], **index[1])

    def tearDown(self):
        """
        Closes the connection
        """
        self.connection.close()

    def pullIds(self):
        """
        Pulls all document Ids and returns as a shuffled list
        """
        ids = [tdoc["_id"] for tdoc in self.collection.find({}, {"_id":1})]
        random.shuffle(ids)
        return ids

    def checkIdExistence(self, bid, field="_id"):
        """
        Checks for the Existence of an Id
        input:
            Document Id (as ObjectId or string)
        output:
            True for existence
            False for non-existence
        """
        # Check the type
        bid = self._formatId(bid)
        # Perform the check
        if self.collection.find_one({field: bid}) is None:
            return False
        else:
            return True

    def pullDocument(self, bid, field="_id"):
        """
        Pulls a document and returns a dictionary, if no document
        returns none
        input:
            bson_id
        output:
            document
        """
        bid = self._formatId(bid)
        tdoc = self.collection.find_one({field: bid})
        return tdoc
