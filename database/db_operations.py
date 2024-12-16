from typing import List, Dict, Any
from pymongo import ASCENDING
from database.mongo_client import MongoDBClient
from models.variant import Variant

class VariantDBOperations:
    BATCH_SIZE = 1000  #procesa los registros en lotes de 1000

    def __init__(self):
        self.client = MongoDBClient()
        self.client.connect()
        self._create_indexes()

    def _create_indexes(self):
        #creacion de indices para mejorar el rendimiento en las consultas 
        try:
            self.client.collection.create_index([
                ("chromosome", ASCENDING),
                ("position", ASCENDING)
            ])
            self.client.collection.create_index("variant_id")
            print("Database indexes created successfully")
        except Exception as e:
            print(f"Error creating indexes: {str(e)}")

    def insert_batch(self, variants: List[Variant], collection_name: str = None) -> int:
        """
        Insert a batch of variants into MongoDB
        Returns the total number of successfully inserted variants
        """
        total_inserted = 0
        current_batch = []

        try:
            # Use the specified collection if provided, otherwise use the default
            collection = self.client.db[collection_name] if collection_name else self.client.collection

            for variant in variants:
                current_batch.append(variant)
                
                # Process batch when it reaches the batch size
                if len(current_batch) >= self.BATCH_SIZE:
                    inserted = collection.insert_many([v.to_dict() for v in current_batch])
                    total_inserted += len(inserted.inserted_ids)
                    current_batch = []  # Clear the batch
                    print(f"Inserted {len(inserted.inserted_ids)} variants...")

            # Process any remaining variants
            if current_batch:
                inserted = collection.insert_many([v.to_dict() for v in current_batch])
                total_inserted += len(inserted.inserted_ids)
                print(f"Inserted final {len(inserted.inserted_ids)} variants...")

            return total_inserted

        except Exception as e:
            print(f"Error during batch insertion: {str(e)}")
            return total_inserted

    def close(self):
        """Close database connection"""
        self.client.close()