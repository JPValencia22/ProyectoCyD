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

    def insert_batch(self, variants: List[Variant]) -> int:
       # inserta un lote de variantes en la base de datos y devuelve el numero total de las insertadas satisfactoriamente
        total_inserted = 0
        current_batch = []

        try:
            for variant in variants:
                current_batch.append(variant)
                
                #se procesa el lote cuando se alcanza el tamaño del mismo
                if len(current_batch) >= self.BATCH_SIZE:
                    inserted = self.client.insert_variants(current_batch)
                    total_inserted += inserted
                    current_batch = []  #limpiar el lote
                    print(f"Inserted {inserted} variants...")

            # procesa las variantes que quedan
            if current_batch:
                inserted = self.client.insert_variants(current_batch)
                total_inserted += inserted
                print(f"Inserted final {inserted} variants...")

            return total_inserted

        except Exception as e:
            print(f"Error during batch insertion: {str(e)}")
            return total_inserted

    def get_variant_count(self) -> int:
        #obtiene el recuento total de variantes en la base de datos
        try:
            return self.client.collection.count_documents({})
        except Exception as e:
            print(f"Error getting variant count: {str(e)}")
            return 0

    def get_variants_for_display(self, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        #Recuperar variantes formateadas para su visualización en el frontend
        try:
            variants = self.client.collection.find({}).skip(skip).limit(limit)
            return [Variant.get_display_columns(variant) for variant in variants]
        except Exception as e:
            print(f"Error retrieving variants: {str(e)}")
            return []

    def get_column_headers(self) -> List[str]:
        #Obtener encabezados de columna para visualización frontend
        try:
            first_variant = self.client.collection.find_one()
            if first_variant:
                return Variant.get_display_columns(first_variant)
            return []
        except Exception as e:
            print(f"Error getting column headers: {str(e)}")
            return []

    def close(self):
        #cerrar la conexión de la base de datos
        self.client.close()