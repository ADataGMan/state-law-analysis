#!/usr/bin/env python3
################## Libraries ##################
import requests
import bs4
import pymongo
import datetime
import time
import urllib.parse
import multiprocessing
from multiprocessing import pool

################## Misc ##################
cores = multiprocessing.cpu_count()

run_date_time = datetime.datetime.now()


################## DB Config ##################
database_url = 'mongodb://localhost:27017'

db_client = pymongo.mongo_client.MongoClient(database_url)
database = db_client['retrieval']

awaiting_retrieval_collection = database["awaiting_retrieval"]
retrieved_collection = database["retrieved"]
unavailable_collection = database["unavailable"]
state_collection = database['state_top_level_url']

################## Functions ##################

def get_request_content(url, state_code, retries=0, request_delay=3):
    try:
        time.sleep(request_delay)
        content = requests.get(url)
        return content
    except:
        if retries >= 3:

            unavailable_collection.insert_one(
                {"url":url, "state_code":state_code}
            )
            awaiting_retrieval_collection.remove(
                {"url":url}
            )
            return
        else:
            get_request_content(url, retries + 1, request_delay * 2)

def retrieve_data():
      
    for state in state_collection.find({},{'_id':0}):
        
        root_url = urllib.parse.urlparse(state['url']).hostname

        if state['state_code'] not in database.collection_names():
            awaiting_retrieval_collection.insert_one(
                {"url":state['url'],"state_code":state['state_code']}
                )
        
        if __name__ == '__main__':
            retrieval_list = list(awaiting_retrieval_collection.find(
                {'state_code':state['state_code']}
                ,{'url':1,'_id':0,'state_code':1}
                ))

            while retrieval_list:
                with pool.Pool(cores) as p:

                    requests = list()
                    for retrieval_url in retrieval_list:

                        request_record = (
                            retrieval_url['url']
                            ,root_url
                            ,state['state_code']
                            )
                        requests.append(request_record)

                    p.starmap(retrieve_binary,requests)
                    p.close()
                    p.join()
                retrieval_list = list(awaiting_retrieval_collection.find(
                    {'state_code':state['state_code']}
                    ,{'url':1,'_id':0,'state_code':1}
                    ))

def retrieve_binary(request_url, root_url, request_state_code):
    
    state_db = database[request_state_code]
    retrieved_list = list(map(
        lambda x:x['url']
        ,retrieved_collection.find({},{'url':1,'_id':0})
        ))
    
    if (request_url in retrieved_list) \
        and (urllib.parse.urlparse(request_url).hostname == root_url):

        raw_content = None

        request_start_date_time = datetime.datetime.now()
        raw_content = get_request_content(request_url, request_state_code)
        request_end_date_time = datetime.datetime.now()
    
        if not raw_content: return

        status_code = raw_content.status_code
        status_reason = raw_content.reason

        content = None

        if status_code == 200:
            content = raw_content.content
            htmlparser = bs4.BeautifulSoup(content,'html.parser')
            link_url = None
            next_link_list = list()
            for link in htmlparser.find_all('a'):
                hrf = link.get('href')

                link_url = urllib.parse.urljoin(request_url,hrf)
                next_link_list.append(link_url)
                awaiting_retrieval_collection.insert_one(
                    {"url":link_url
                    ,'state_code':request_state_code}
                    )
        
        record = {
            "version_date_time":run_date_time,
            "state_code":request_state_code,
            "request_url":request_url,
            "request_start_date_time":request_start_date_time,
            "request_end_date_time":request_end_date_time,
            "status_code":status_code,
            "status_reason":status_reason,
            "next_link_list":next_link_list,
            "content":content
        }

        state_db.insert_one(record)
        retrieved_collection.insert_one(
            {'url':request_url
            ,'state_code':request_state_code}
        )
        awaiting_retrieval_collection.remove(
            {"url":request_url}
        )

retrieve_data()