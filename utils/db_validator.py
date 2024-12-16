import subprocess
import sys
from pymongo import MongoClient

def check_mongodb_running():
    #verifica si mongo esta ejecutandose localmente
    try:
        client = MongoClient('localhost', 27017, serverSelectionTimeoutMS=2000)
        client.server_info()
        return True
    except Exception:
        return False
print("MongoDB is running correctly on localhost:27017")