from pprint import pprint
from pymongo import MongoClient
import requests
import bs4
import pymongo
import datetime
import time
import urllib.parse
import re
import html
from dateutil import parser as Date_Parser


from Utility.string import StrUtil

################## Misc ##################
config_request_delay = 3

test_url = 'http://www.gencourt.state.nh.us/rsa/html/I/3-B/3-B-1.htm'
state_code = 'NH'

run_date_time = datetime.datetime.now()
################## DB Config ##################
database_url = 'mongodb://localhost:27017'

db_client = pymongo.mongo_client.MongoClient(database_url)
database = db_client['retrieval']

awaiting_retrieval_collection = database["awaiting_retrieval"]
retrieved_collection = database["retrieved"]
unavailable_collection = database["unavailable"]
state_collection = database['state_top_level_url']

################## Global Variables ##################

new_record = dict()

tokenized_list = list()

def get_request_content(url, state_code, retries=0, request_delay=3):
    try:
        time.sleep(request_delay)
        content = requests.get(url)
        result = None
        if content:
            result = {"content":content, "request_delay":request_delay}
        return result
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
            get_request_content(url, state_code, retries + 1, request_delay * 2)

def retrieve_binary(request_url, request_state_code):

    state_db = database[request_state_code]

    raw_content = None
    request_start_date_time = datetime.datetime.now()
    raw_content = get_request_content(
        request_url
        ,request_state_code
        ,config_request_delay
        )
    request_end_date_time = datetime.datetime.now()

    if raw_content:
        status_code = raw_content['content'].status_code
        status_reason = raw_content['content'].reason

        content = None

        if status_code == 200:
            content = raw_content['content'].content
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
            "request_delay_seconds":raw_content['request_delay'],
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

def extract_record():
    # import bs4
    # Retrieve all records in the state collection
    # and don't return _id or url
    retrieval_state = database[state_code]

    for binary_record in retrieval_state.find():
        parse_record(binary_record)
        # insert_record(state_code)

def parse_record(binary_record):

    if binary_record is None:
        return None # Insert record into failed record dataset.

    # print(binary_record['content'])
    if binary_record.get('content') is None:
        return None # Insert record into skipped record dataset.

    document = bs4.BeautifulSoup(
        binary_record['content']
        ,'html.parser'
        )

    for tag in document.find_all('meta'):
        tag_name = tag['name'].lower()
        # if tag_name == 'sourcenote':
        #     extract_sourcenote_metadata(tag)

        if tag_name == 'titlename':
            extract_title_metadata(tag)
        elif tag_name == 'chapter':
            extract_chapter_metadata(tag)
        elif tag_name == 'sectiontitle':
            extract_sectiontitle_metadata(tag)
        elif tag_name == 'sourcenote':
            extract_sourcenote_metadata(tag)
        elif tag_name == 'codesect':
            extract_codesect_metadata(tag)
    
    extract_collection = database["extract"]
    pprint(new_record)
    extract_collection.insert_one(new_record)

def extract_title_metadata(tag):
    tag_content = tag['content']
    title_num_regex = re.compile(
        'title (\\S+)'
        ,re.IGNORECASE
    )
    title_search = title_num_regex.search(tag_content)

    title_numeral = title_search.group(1).strip()
    title_number = StrUtil.get_title_number(title_numeral)
    title_name = tag_content.split(title_search.group(0))[1].strip()

    new_record.update({
        "title_number_text":title_numeral,
        "title_number":title_number,
        "title_name":title_name,
        "title_content":tag_content
    })

def extract_chapter_metadata(tag):
    tag_content = tag['content']
    chapter_num_regex = re.compile(
        'chapter (\\S+)'
        ,re.IGNORECASE
    )
    chapter_search = chapter_num_regex.search(tag_content)

    chapter_number_text = chapter_search.group(1).strip()
    chapter_num_list = chapter_number_text.split('-')

    major_chapter = chapter_num_list[0]
    minor_chapter = 0

    if len(chapter_num_list) >= 2:
        minor_chapter = StrUtil.char_to_num(chapter_num_list[1])
    
    chapter_number = float(str(major_chapter)+'.'+str(minor_chapter))
    
    chapter_name = tag_content.split(chapter_search.group(0))[1].strip()

    new_record.update({
        "chapter_name": chapter_name,
        "chapter_number": chapter_number,
        "chapter_number_text": chapter_number_text,
        "chapter_content":tag_content
    })
    
def extract_sectiontitle_metadata(tag):
    tag_content = tag['content']
    section_num_regex = re.compile(
        ':(\\S+)'
        ,re.IGNORECASE
    )
    section_search = section_num_regex.search(tag_content)

    section_number_text = section_search.group(1).strip()

    section_num_list = section_number_text.split('-')

    major_section = section_num_list[0]
    minor_section = 0

    if len(section_num_list) >= 2:
        minor_section = StrUtil.char_to_num(section_num_list[1])
    
    section_number = float(str(major_section)+'.'+str(minor_section))
    
    section_name = tag_content.split(section_search.group(0))[1].strip()

    new_record.update({
        "section_name": section_name,
        "section_number": section_number,
        "section_number_text": section_number_text,
        "section_content": tag_content
    })

def extract_sourcenote_metadata(tag):
    tag_content = tag['content']

    # print(type(tag_content))
    # print(tag_content)

    source_type = 'Source'

    if tag_content == "":
        return
    elif not tag_content.lower().find('repealed') == -1:
        source_type = 'Repealed'
    
    source_text = re.search(
        ',(.+), eff'
        ,tag_content
        ,flags=re.IGNORECASE 
        # use | and another re.option to add more flags
    ).group(1).strip()

    source_date_text = re.search(
        'eff.(.+)\\W\\D'
        ,tag_content
        ,re.IGNORECASE
    ).group(1).strip()

    source_date = Date_Parser.parse(source_date_text)

    print(source_date)
    print(source_date_text)

    new_record.update({
        "source_type":source_type,
        "source_effective_date":source_date,
        "source_text":source_text,
        "source_content":tag_content
    })  

def extract_codesect_metadata(tag):
    tag_content = tag['content']

    break_regex = '<.*?br.*?>'

    if not tag_content.lower().find('repealed') == -1:
        extract_sourcenote_metadata(tag)

    content = tag_content

    if re.search(break_regex, tag_content, re.IGNORECASE):
        content = re.sub(break_regex, '\n', tag_content, flags=re.IGNORECASE)
    
    content = content.strip()
    
    new_record.update({
        "law_content_raw":tag_content,
        "law_content": content
    })

def run_tokenizer():
    extracted = database['extract']

    for record in extracted.find():
        ff = record['law_content']
        f = tokenize(ff,1)
        tokenized_list.append(f)
        print(ff)



def tokenize(text,text_id,line_id=0):
    #text = re.sub("[^a-zA-Z]"," ", str(text))
    token_counter= 0
    data = list()
    l = [item for item in map(str.strip, re.split("(\W)",text)) if len(item)>0]
    for token in l:
        lower_token = token.lower()

        row ={
              "textID":text_id,
              "lineID":'L00000'+str(line_id),
              "tokenID":'T000000'+str(token_counter),
              "tokenRaw":token,
              "tokenLower":lower_token
             }
        data.append(row)
        token_counter=token_counter+1
    return data


# retrieve_binary(test_url,state_code)

# extract_record()

run_tokenizer()
pprint(tokenized_list)