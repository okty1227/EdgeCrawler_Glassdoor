#use docker exec -it romantic_kowalevski  mongosh to initiate mongosh
import pymongo
from datetime import datetime



async def load_to_mongo_db(loaded_data,port_link,collection_name:str):
    
    def create_collectionname_by_date():
        current_date_string = datetime.now().date().strftime("%Y%m%d")
        current_dt = collection_name + '_' + str(current_date_string)
        name_ct = 0
        if current_dt in db.list_collection_names():
            name_ct+=1
            return current_dt + f'_{name_ct}'
        return current_dt
    
    client = pymongo.MongoClient(port_link)

    db = client['glassdoor_job']

    collection_set_name = create_collectionname_by_date()
    collection = db[collection_set_name]
        
    for position in loaded_data:
        collection.insert_one(position)