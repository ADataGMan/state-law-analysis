# # This code checks to see if this module is being run directly. 
# # If so, it registers the top level directory of SLA so that 
# # sibling modules can be used.
# if __name__ == '__main__':
#     from sys import path
#     from os.path import dirname
#     parent_dir = dirname(path[0]).rpartition('\\')[0]
#     # dirname_example: 'e:\Python\state_law_analysis\state_law_analysis'
#     # parent_dir_example: 'e:\Python\state_law_analysis'
#     if parent_dir not in path:
#         path.append(parent_dir)

# from state_law_analysis.Utility.string import StrUtil





# def get_request_content(url, state_code, retries=0, request_delay=3):
#     try:
#         time.sleep(request_delay)
#         content = requests.get(url)
#         result = None
#         if content:
#             result = {"content":content, "request_delay":request_delay}
#         return result
#     except:
#         if retries >= 3:

#             unavailable_collection.insert_one(
#                 {"url":url, "state_code":state_code}
#             )
#             awaiting_retrieval_collection.remove(
#                 {"url":url}
#             )
#             return
#         else:
#             get_request_content(url, state_code, retries + 1, request_delay * 2)

# def retrieve_data():
      
#     for state in state_collection.find({},{'_id':0}):
        
#         root_url = urllib.parse.urlparse(state['url']).hostname

#         if state['state_code'] not in database.collection_names():
#             awaiting_retrieval_collection.insert_one(
#                 {"url":state['url'],"state_code":state['state_code']}
#                 )
        
#         if __name__ == '__main__':
#             retrieval_list = list(awaiting_retrieval_collection.find(
#                 {'state_code':state['state_code']}
#                 ,{'url':1,'_id':0,'state_code':1}
#                 ))

#             while retrieval_list:
#                 with pool.Pool(cores) as p:

#                     requests = list()
#                     for retrieval_url in retrieval_list:

#                         request_record = (
#                             retrieval_url['url']
#                             ,root_url
#                             ,state['state_code']
#                             )
#                         requests.append(request_record)

#                     p.starmap(retrieve_binary,requests)
#                     p.close()
#                     p.join()
#                 retrieval_list = list(awaiting_retrieval_collection.find(
#                     {'state_code':state['state_code']}
#                     ,{'url':1,'_id':0,'state_code':1}
#                     ))

# def retrieve_binary(request_url, root_url, request_state_code):

#     request_root = urllib.parse.urlparse(request_url).hostname
#     state_db = database[request_state_code]

#     retrieved_list = list(map(
#         lambda x:x['url']
#         ,retrieved_collection.find({},{'url':1,'_id':0})
#         ))
    
#     if (request_url not in retrieved_list) \
#         and (request_root == root_url):

#         raw_content = None
#         request_start_date_time = datetime.datetime.now()
#         raw_content = get_request_content(
#             request_url
#             ,request_state_code
#             ,config_request_delay
#             )
#         request_end_date_time = datetime.datetime.now()
    
#         if raw_content:
#             status_code = raw_content['content'].status_code
#             status_reason = raw_content['content'].reason

#             content = None

#             if status_code == 200:
#                 content = raw_content['content'].content
#                 htmlparser = bs4.BeautifulSoup(content,'html.parser')
#                 link_url = None
#                 next_link_list = list()
#                 for link in htmlparser.find_all('a'):
#                     hrf = link.get('href')

#                     link_url = urllib.parse.urljoin(request_url,hrf)
#                     next_link_list.append(link_url)
#                     awaiting_retrieval_collection.insert_one(
#                         {"url":link_url
#                         ,'state_code':request_state_code}
#                         )
            
#             record = {
#                 "version_date_time":run_date_time,
#                 "state_code":request_state_code,
#                 "request_url":request_url,
#                 "request_start_date_time":request_start_date_time,
#                 "request_end_date_time":request_end_date_time,
#                 "request_delay_seconds":raw_content['request_delay'],
#                 "status_code":status_code,
#                 "status_reason":status_reason,
#                 "next_link_list":next_link_list,
#                 "content":content
#             }

#             state_db.insert_one(record)
#             retrieved_collection.insert_one(
#                 {'url':request_url
#                 ,'state_code':request_state_code}
#             )

#     awaiting_retrieval_collection.remove(
#         {"url":request_url}
#     )