
################## Libraries ##################
import requests
import bs4
import pymongo
import datetime
import time
import urllib.parse
import multiprocessing
from multiprocessing import pool

################## DB Config ##################
db_client = pymongo.mongo_client.MongoClient('mongodb://localhost:27017')
db_retrieval = db_client['retrieval']
db_awaiting_retrieval = db_retrieval["awaiting_retrieval"]
db_retrieved = db_retrieval["retrieved"]

################## Misc ##################
retrieved_url_list = list()
awaiting_retrieval_list = list()

state_abbreviation_code = 'nh'

nh_top_level_url = 'http://www.gencourt.state.nh.us/rsa/html/nhtoc.htm'

################## Startup Operations ##################
version_date_time = datetime.datetime.now()
url_root = urllib.parse.urlparse(nh_top_level_url).hostname
cores = 1 #multiprocessing.cpu_count()

# check for root to avoid escaping site boundaries
# set up storage for lists





def get_request(url,retries=0, recover_seconds=3):
    try:
        content = requests.get(url)
        return content
    except:
        if retries >= 3:
            return
        else:
            time.sleep(recover_seconds)
            get_request(url, retries + 1, recover_seconds * 2)


def raw_retrieval(request_url, root_url = None, functional_delay = 3):

    if not root_url:
        url_root = urllib.parse.urlparse(request_url).hostname

    if request_url not in retrieved_url_list and \
        urllib.parse.urlparse(request_url).hostname == url_root:

        time.sleep(functional_delay)

        raw_content = None

        request_start_date_time = datetime.datetime.now()
        raw_content = get_request(request_url)
        request_end_date_time = datetime.datetime.now()

        if not raw_content: return

        db_retrieved.insert_one({"url":request_url})
        db_awaiting_retrieval.remove({"url":request_url})

        # retrieved_url_list.append(request_url)
        # awaiting_retrieval_list.remove(request_url)

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

                link_url = urllib.parse.urljoin(request_url,hrf)
                next_link_list.append(link_url)
                db_awaiting_retrieval.insert_one({"url":link_url})
                # awaiting_retrieval_list.append(link_url)
        
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

        dbc = db_retrieval[state_abbreviation_code]
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