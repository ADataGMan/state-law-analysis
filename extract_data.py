import re
import bs4
import datetime
import html
import pymongo

from Utility.Utility_Functions import StringUtility

test = {'request_url':'http://www.gencourt.state.nh.us/rsa/html/I/3-B/3-B-1.htm'}

database_url = 'mongodb://localhost:27017'

db_client = pymongo.mongo_client.MongoClient(database_url)
retrieval_db = db_client['retrieval']
tokenized_db = db_client['tokenized']
state_collection =retrieval_db['state_top_level_url']

def tokenize_record():
    for state in state_collection.find({}, {'_id':0,'url':0}):
        state_code = state['state_code']
        retrieval_state = retrieval_db[state_code]

        for binary_record in retrieval_state.find(test):
            parse_record(binary_record)

def parse_record(binary_record):

    new_record = dict()

    document = bs4.BeautifulSoup(
        binary_record['content']
        ,'html.parser'
        )

    for tag in document.find_all('meta'):
        tag_name = tag['name'].lower()
        if tag_name == 'sectiontitle':
            extract_sectiontitle_metadata(tag)

        if tag_name == 'titlename':
            new_record.update(extract_title_metadata(tag))
        elif tag_name == 'chapter':
            new_record.update(extract_chapter_metadata(tag))
        elif tag_name == 'sectiontitle':
            new_record.update(extract_sectiontitle_metadata(tag))
        # elif tag_name == 'sourcenote':
        #     new_record.update(extract_sourcenote_metadata(tag))
        # elif tag_name == 'codesect':
        #     new_record.update(extract_codesect_metadata(tag))

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

    return {
        "title_numeral":title_numeral,
        "title_number":title_number,
        "title_name":title_name
    }

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

    return {
        "chapter_name": chapter_name,
        "chapter_number": chapter_number,
        "chapter_number_text": chapter_number_text
    }
    
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

    return {
        "section_name": section_name,
        "section_number": section_number,
        "section_number_text": section_number_text
    }

def extract_sourcenote_metadata(tag):
    pass

def extract_codesect_metadata(tag):
    pass

tokenize_record()