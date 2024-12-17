from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import lru_cache
from typing import List, Dict, Any
from pymongo import ASCENDING, TEXT, MongoClient
from database.mongo_client import MongoDBClient
from models.variant import Variant


class VariantDBOperations:
    CHUNK_SIZE = 1000  # Tamaño más pequeño para procesamiento paralelo
    

    def __init__(self):
        self.client = MongoClient('mongodb://localhost:27017/')
        self.db = self.client['vcf_database']
        self.collection = self.db['variants']
        self.executor = ThreadPoolExecutor(max_workers=4)
        self._create_indexes()

    # MÉTODO PARALLELIZADO PARA INSERCIÓN POR LOTES
    def insert_batch(self, variants: List[Variant], collection_name: str = None) -> int:
        
        total_inserted = 0
        collection = self.db[collection_name] if collection_name else self.collection

        def process_batch(batch):
            """Inserta un lote individual en MongoDB."""
            try:
                inserted = collection.insert_many([v.to_dict() for v in batch])
                print(f"Inserted {len(inserted.inserted_ids)} variants...")
                return len(inserted.inserted_ids)
            except Exception as e:
                print(f"Error inserting batch: {str(e)}")
                return 0

        # Dividir las variantes en chunks
        futures = []
        for i in range(0, len(variants), self.CHUNK_SIZE):
            batch = variants[i:i + self.CHUNK_SIZE]
            future = self.executor.submit(process_batch, batch)
            futures.append(future)

        # Recolectar los resultados de los futuros
        for future in as_completed(futures):
            total_inserted += future.result()

        print(f"Total inserted: {total_inserted} variants.")
        return total_inserted

    def _process_chunk(self, skip: int, limit: int, filters: dict = None) -> List[Dict]:
        query = filters or {}
        cursor = self.collection.find(query, {'_id': 0}).skip(skip).limit(limit)
        return list(cursor)

    @lru_cache(maxsize=128)
    def get_paginated_variants(self, page, per_page):
        skip = (page - 1) * per_page
        chunks = []
        futures = []

        # Dividir la consulta en chunks
        for i in range(0, per_page, self.CHUNK_SIZE):
            chunk_skip = skip + i
            chunk_limit = min(self.CHUNK_SIZE, per_page - i)
            future = self.executor.submit(self._process_chunk, chunk_skip, chunk_limit)
            futures.append(future)

        # Recolectar resultados
        for future in as_completed(futures):
            chunks.extend(future.result())

        # Transformar resultados
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
            for variant in chunks
        ]

        total = self.collection.estimated_document_count()
        return result, total

    def search_variants(self, query_params, page, per_page):
        skip = (page - 1) * per_page
        search_filters = {}
        chunks = []
        futures = []

        # Construir filtros
        if 'Chrom' in query_params:
            search_filters['chromosome'] = query_params['Chrom']
        if 'Filter' in query_params:
            search_filters['filter'] = query_params['Filter']
        if 'Info' in query_params:
            search_filters['$text'] = {'$search': query_params['Info']}
        if 'Format' in query_params:
            search_filters['format'] = query_params['Format']

        # Dividir la consulta en chunks
        for i in range(0, per_page, self.CHUNK_SIZE):
            chunk_skip = skip + i
            chunk_limit = min(self.CHUNK_SIZE, per_page - i)
            future = self.executor.submit(
                self._process_chunk,
                chunk_skip,
                chunk_limit,
                search_filters
            )
            futures.append(future)

        # Recolectar resultados
        for future in as_completed(futures):
            chunks.extend(future.result())

        # Transformar resultados
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
            for variant in chunks
        ]

        total = self.collection.count_documents(search_filters)
        return result, total

    def _create_indexes(self):
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

    def close(self):
        """Close database connection and executor"""
        self.executor.shutdown(wait=True)
        self.client.close()
