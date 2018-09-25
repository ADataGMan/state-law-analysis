import requests
import bs4
import pymongo
import datetime
import time
from urllib.parse import urljoin

from multiprocessing import pool
import multiprocessing

version_date_time = datetime.datetime.now()

dbclient = pymongo.mongo_client.MongoClient('mongodb://localhost:27017')
dbcollection = dbclient['legal_raw']

retrieved_url_list = list()
awaiting_retrieval_list = list()



state_abbreviation_code = 'nh'

nh_top_level_url = 'http://www.gencourt.state.nh.us/rsa/html/nhtoc.htm'
nh_root = 'http://www.gencourt.state.nh.us/rsa/html/'

# check for root to avoid escaping site boundaries

functional_delay = 1
cores = multiprocessing.cpu_count()


def raw_retrieval(request_url):

    if request_url not in retrieved_url_list:
        time.sleep(functional_delay)

        raw_content = None

        request_start_date_time = datetime.datetime.now()
        raw_content = requests.get(request_url)
        request_end_date_time = datetime.datetime.now()

        retrieved_url_list.append(request_url)
        awaiting_retrieval_list.remove(request_url)

        status_code = raw_content.status_code
        status_reason = raw_content.reason

        content = None

        if status_code == 200:
            content = raw_content.content
            soup = bs4.BeautifulSoup(content,'html.parser')
            link_url = None
            next_link_list = list()
            for link in soup.find_all('a'):
                hrf = link.get('href')

                link_url = urljoin(request_url,hrf)
                next_link_list.append(link_url)
                awaiting_retrieval_list.append(link_url)
        
        record = {
            "version_date_time":version_date_time,
            "state_abbreviation_code":state_abbreviation_code,
            "request_url":request_url,
            "request_start_date_time":request_start_date_time,
            "request_end_date_time":request_end_date_time,
            "status_code":status_code,
            "status_reason":status_reason,
            "next_link_list":next_link_list,
            "content":content
        }

        dbc = dbcollection[state_abbreviation_code]
        dbc.insert_one(record)

awaiting_retrieval_list.append(nh_top_level_url)

if __name__ == '__main__':

    while awaiting_retrieval_list:
        arl = awaiting_retrieval_list.copy()

        p = pool.Pool(cores)

        p.map(raw_retrieval, arl)
        p.close()
        p.join()

        # for rurl in arl:
        #     raw_retrieval(rurl)