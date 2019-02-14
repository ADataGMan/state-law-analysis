#TODO Make Multiprocessing Optional

import multiprocessing
from pymongo import MongoClient

from environment import env_config

class Config:

    def __init__(self):
        self.cores = multiprocessing.cpu_count()
        

    @property
    def cores(self):
        return self.__cores

    @cores.setter
    def cores(self, cores):
        self.__cores = cores

        # transform_db = db_client['transform']
        # load_db = db_client['load']

class MongoConfig:

    #Test ME!!

    def __init__(self,**env_config):
        self.MongoConnect(**env_config)
    
    def MongoConnect(self,**env):
        """
        Connect to each MongoDB Database to be used for handling data.
        Define each operational collection used to store documents
        """
        db_client = MongoClient(env["mongo_url"])
        extract_db = db_client['extract']

        mdb = {
            "db_client":db_client
            ,"extract_db":db_client['extract']
            ,"awaiting_retrieval_collection":extract_db["awaiting_retrieval"]
            ,"retrieved_collection":extract_db["retrieved"]
            ,"unavailable_collection":extract_db["unavailable"]
            ,"state_collection":extract_db['state_list']
        }

        # extract_db = db_client['extract']
        # awaiting_retrieval_collection = extract_db["awaiting_retrieval"]
        # retrieved_collection = extract_db["retrieved"]
        # unavailable_collection = extract_db["unavailable"]
        # state_collection = extract_db['state_list']

        return mdb

conf = Config()

print(conf.cores)