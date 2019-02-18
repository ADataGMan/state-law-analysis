mongo_config = {
    "mongo_url":"mongodb://localhost:27017"
}

db_collection = {"extract_db":
    [
        "awaiting_retrieval_collection"
        ,"retrieved_collection"
        ,"unavailable_collection"
        ,"state_collection"
    ]
}



    # mdb = {
    #     "db_client":db_client
    #     ,"extract_db":db_client['extract']
    #     ,"awaiting_retrieval_collection":extract_db["awaiting_retrieval"]
    #     ,"retrieved_collection":extract_db["retrieved"]
    #     ,"unavailable_collection":extract_db["unavailable"]
    #     ,"state_collection":extract_db['state_list']
    # }