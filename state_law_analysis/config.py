#TODO Make Multiprocessing Optional

import multiprocessing
from pymongo import MongoClient

class MongoHelper:

    db_names_dict = dict()
    db_conn_config = dict()

    def __init__(self,db_config,db_names):
        self.db_client = MongoClient(
            host=db_config["host"]
            )
        self.connect_to_many(db_names)


    def connect_to_one(self,db_conn_config,db_name):
        db_connection = self.db_client[db_name]
        return db_connection

    def connect_to_many(self,db_names):
        for db_name in db_names:
            db_client = self.connect_to_one(db_name)
            self.db_names_dict[db_name] = db_client
    def retrieve_collection(self):
        pass

import config_params

m = MongoHelper(config_params.db_collection)

# first thing is to get db_names 
# db_names = ['test','test2','test3']
# m = MongoHelper(db_names)
# print(m.db_names_dict)

