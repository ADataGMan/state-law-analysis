import re
import bs4
import datetime
import html
import pymongo
from dateutil import parser as Date_Parser

from Utility.Utility_Functions import StringUtility

test = {'request_url':
'http://www.gencourt.state.nh.us/rsa/html/I/3-B/3-B-1.htm' #normal
# 'http://www.gencourt.state.nh.us/rsa/html/II/30/30-5.htm' #repealed
# 'http://www.gencourt.state.nh.us/rsa/html/I/6-B/6-B-4.htm' #complex content
# 'http://www.gencourt.state.nh.us/rsa/html/nhtoc.htm' #table of contents
# 'http://www.gencourt.state.nh.us/rsa/html/NHTOC/NHTOC-I.htm' #table of contents Title 1
# 'http://www.gencourt.state.nh.us/rsa/html/NHTOC/NHTOC-I-1.htm' #table of contents title 1 chapter 1
}

database_url = 'mongodb://localhost:27017'

db_client = pymongo.mongo_client.MongoClient(database_url)
retrieval_db = db_client['retrieval']
extract_db = db_client['extract']
state_collection =retrieval_db['state_top_level_url']

new_record = dict()

def extract_record():
    for state in state_collection.find({}, {'_id':0,'url':0}):
        state_code = state['state_code']
        retrieval_state = retrieval_db[state_code]

        for binary_record in retrieval_state.find(test):
            parse_record(binary_record)
            insert_record(state_code)

def parse_record(binary_record):

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

    print(new_record)

def extract_title_metadata(tag):
    tag_content = tag['content']
    title_num_regex = re.compile(
        'title (\\S+)'
        ,re.IGNORECASE
    )
    title_search = title_num_regex.search(tag_content)

    title_numeral = title_search.group(1).strip()
    title_number = StringUtility.get_title_number(title_numeral)
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
        minor_chapter = StringUtility.char_to_num(chapter_num_list[1])
    
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
        minor_section = StringUtility.char_to_num(section_num_list[1])
    
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
    ).group(1).strip()

    source_date = Date_Parser.parse(source_date_text)

    new_record.update({
        "source_type":source_type,
        "source_effective_date":source_date,
        "source_text":source_text,
        "source_content":tag_content
    })  

def extract_codesect_metadata(tag):
    tag_content = tag['content']

    if not tag_content.lower().find('repealed') == -1:
        extract_sourcenote_metadata(tag)

    new_record.update({
        "law_content":tag_content
    })

def insert_record(state_code):
    if new_record:
        state_extract = extract_db[state_code]
        state_extract.insert_one(new_record)

extract_record()