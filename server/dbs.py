from pymongo import MongoClient
import gridfs

MONGO_DATABASE = 'haystack'
FILES_COLLECTION = 'files'
CLIENTS_COLLECTION = 'clients'
CASES_COLLECTION = 'cases'
SAVED_SEARCHES = 'savedsearches'

client = MongoClient()
db = client[MONGO_DATABASE]
files = db[FILES_COLLECTION]
clients = db[CLIENTS_COLLECTION]
casescollection = db[CASES_COLLECTION]
savedsearches = db[SAVED_SEARCHES]
gfs = gridfs.GridFS(db)

