import re
import bs4
import roman
import datetime
import html
import pymongo
from pprint import pprint

test = {'request_url':'http://www.gencourt.state.nh.us/rsa/html/I/3-B/3-B-1.htm'}

database_url = 'mongodb://localhost:27017'

db_client = pymongo.mongo_client.MongoClient(database_url)
retrieval_db = db_client['retrieval']
tokenized_db = db_client['tokenized']
state_collection =retrieval_db['state_top_level_url']

def parse_record(binary_record):
    document = bs4.BeautifulSoup(
        binary_record['content']
        ,'html.parser'
        )

    for tag in document.find_all('meta'):
        # print(tag['content'])

        if str.lower(tag['name']) == "titlename":
            tag_content = tag['content']
            title_num_regex = re.compile(
                'title (\\S+)'
                ,re.IGNORECASE
            )
            title_numeral = (
                title_num_regex.search(tag_content).group(1)
                ).strip()
            print(title_numeral)

def tokenize_record():
    for state in state_collection.find({}, {'_id':0,'url':0}):
        state_code = state['state_code']
        retrieval_state = retrieval_db[state_code]

        for binary_record in retrieval_state.find(test):
            parse_record(binary_record)

tokenize_record()