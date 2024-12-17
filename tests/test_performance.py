import time
from random import randint, choice
from string import ascii_uppercase
from database.db_operations import VariantDBOperations
from models.variant import Variant  # Si es necesario

# Generador de datos ficticios
def generate_mock_variants(num_variants):
    """Genera una lista de variantes ficticias para pruebas."""
    return [
        {
            'chromosome': choice(['1', '2', 'X', 'Y']),
            'position': randint(1, 1_000_000),
            'id': f"rs{randint(1, 1_000_000)}",
            'reference': choice(ascii_uppercase),
            'alternative': choice(ascii_uppercase),
            'quality': round(randint(10, 100) + randint(0, 99) / 100, 2),
            'filter': choice(['PASS', 'FAIL']),
            'info': 'Mock info string',
            'format': 'GT:AD:DP',
            'samples': {}
        }
        for _ in range(num_variants)
    ]

# Prueba de inserción paralelizada
def test_parallel_insert():
    print("Iniciando prueba de inserción paralelizada...")
    db_operations = VariantDBOperations()

    # Generar datos de prueba
    mock_variants = generate_mock_variants(5000)

    # Medir el tiempo de ejecución
    start_time = time.time()
    total_inserted = db_operations.insert_batch(mock_variants)
    end_time = time.time()

    db_operations.close()

    # Resultados
    duration = end_time - start_time
    print(f"Tiempo total: {duration:.2f} segundos")
    print(f"Variantes insertadas: {total_inserted}")
    print(f"Rendimiento: {total_inserted / duration:.2f} variantes/segundo")

# Prueba de inserción secuencial
def test_sequential_insert():
    print("Iniciando prueba de inserción secuencial...")
    db_operations = VariantDBOperations()

    # Generar datos de prueba
    mock_variants = generate_mock_variants(5000)

    # Función para inserción secuencial
    def insert_sequentially(variants):
        collection = db_operations.collection
        inserted_count = 0
        for variant in variants:
            try:
                collection.insert_one(variant)
                inserted_count += 1
            except Exception as e:
                print(f"Error inserting variant: {e}")
        return inserted_count

    # Medir el tiempo de ejecución
    start_time = time.time()
    total_inserted = insert_sequentially(mock_variants)
    end_time = time.time()

    db_operations.close()

    # Resultados
    duration = end_time - start_time
    print(f"Tiempo total: {duration:.2f} segundos")
    print(f"Variantes insertadas: {total_inserted}")
    print(f"Rendimiento: {total_inserted / duration:.2f} variantes/segundo")

if __name__ == "__main__":
    test_parallel_insert()
    print("\n")
    test_sequential_insert()
