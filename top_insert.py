import requests
import bs4
import pymongo
import datetime
import time
import urllib.parse
import multiprocessing
from multiprocessing import pool

db_client = pymongo.mongo_client.MongoClient('mongodb://localhost:27017')
db_retrieval = db_client['retrieval']

record = {
    "NH": 'http://www.gencourt.state.nh.us/rsa/html/nhtoc.htm'
}

dbc = db_retrieval["top_url"]
dbc.insert_one(record)