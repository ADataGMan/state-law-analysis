# from state_law_analysis.config import MongoConnect

state_list = [
    {
        "state_code": "NH",
        "url": "http://www.gencourt.state.nh.us/rsa/html/nhtoc.htm"
    }
]

# Old code to mock up
# import pymongo

# db_client = pymongo.mongo_client.MongoClient('mongodb://localhost:27017')
# db_retrieval = db_client['retrieval']

# record = {
#     "state_code":"NH",
#     "url": 'http://www.gencourt.state.nh.us/rsa/html/nhtoc.htm'
# }

# dbc = db_retrieval["state_top_level_url"]
# dbc.insert_one(record)