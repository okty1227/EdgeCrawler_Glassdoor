#use docker exec -it romantic_kowalevski  mongosh to initiate mongosh
import pymongo


def load_to_mongo_db(loaded_data,port_link):
    client = pymongo.MongoClient(port_link)#"mongodb://localhost:8585/"

    db = client['glassdoor_job']
    collection = db['job4']

    for position in loaded_data:
        collection.insert_one(position)