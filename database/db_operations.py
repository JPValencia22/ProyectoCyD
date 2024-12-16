from typing import List, Dict, Any
from pymongo import ASCENDING, TEXT, MongoClient
from database.mongo_client import MongoDBClient
from models.variant import Variant

class VariantDBOperations:
    BATCH_SIZE = 1000  # procesa los registros en lotes de 1000

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['vcf_database']
        self.collection = self.db['variants']
        self._create_indexes()

    def _create_indexes(self):
        # Creación de índices para mejorar el rendimiento en las consultas
        try:
            self.collection.create_index([('chromosome', ASCENDING)])
            self.collection.create_index([('filter', ASCENDING)])
            self.collection.create_index([('info', TEXT)])
            self.collection.create_index([('format', ASCENDING)])
            self.collection.create_index([
                ('chromosome', ASCENDING),
                ('position', ASCENDING)
            ])
            self.collection.create_index('variant_id')
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
            collection = self.db[collection_name] if collection_name else self.collection

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

    def get_paginated_variants(self, page, per_page):
        skip = (page - 1) * per_page
        cursor = self.collection.find().skip(skip).limit(per_page)
        variants = list(cursor)

        # Transformar los documentos para ser serializables en JSON
        result = [
            {
                'Chrom': variant.get('chromosome'),
                'Pos': variant.get('position'),
                'Id': variant.get('id'),
                'Ref': variant.get('reference'),
                'Alt': variant.get('alternative'),
                'Qual': variant.get('quality'),
                'Filter': variant.get('filter'),
                'Info': variant.get('info'),
                'Format': variant.get('format'),
                'Outputs': variant.get('samples', {})
            }
            for variant in variants
        ]

        total = self.collection.count_documents({})
        return result, total

    def close(self):
        """Close database connection"""
        self.client.close()
