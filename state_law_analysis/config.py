#TODO Make Multiprocessing Optional

import multiprocessing
from pymongo import MongoClient

class MongoHelper:
    db_names_dict = dict()
    def __init__(self,db_names):
        self.connect_to_many(db_names)
    def connect_to_one(self,db_name):
        #connect to db_name
        #return object
        db_client = MongoClient(db_name)
        return db_client

    def connect_to_many(self,db_names):
        for db_name in db_names:
            db_client = self.connect_to_one(db_name)
            self.db_names_dict[db_name] = db_client
    def retrieve_collection(self):
        pass

import config_params

m = MongoHelper(config_params.db)

# first thing is to get db_names 
# db_names = ['test','test2','test3']
# m = MongoHelper(db_names)
# print(m.db_names_dict)

