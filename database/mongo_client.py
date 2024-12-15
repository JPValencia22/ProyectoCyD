from pymongo import MongoClient
from config.db_config import MONGODB_CONFIG

class MongoDBClient:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    def connect(self):
        #establecer la conexión con MongoDB
        try:
            self.client = MongoClient(
                host=MONGODB_CONFIG['host'],
                port=MONGODB_CONFIG['port']
            )
            self.db = self.client[MONGODB_CONFIG['database']]
            self.collection = self.db[MONGODB_CONFIG['collection']]
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise

    def insert_variants(self, variants):
        #Insertar múltiples variantes en MongoDB
        try:
            result = self.collection.insert_many([v.to_dict() for v in variants])
            return len(result.inserted_ids)
        except Exception as e:
            print(f"Error inserting variants: {str(e)}")
            return 0

    def close(self):
        #Cerrar conexión MongoDB
        if self.client:
            self.client.close()