import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.vcf_parser import VCFParser
from models.variant import Variant
from database.db_operations import VariantDBOperations
from utils.progress_tracker import ProgressTracker

def process_single_vcf_file(filename):
    #Procesa un único archivo VCF y almacena sus datos en MongoDB.
    db_ops = VariantDBOperations()
    total_records = 0
    
    try:
        print(f"\nProcessing file: {filename}")
        
        #Analizar el archivo VCF
        records = VCFParser.parse_file(filename)
        
        if not records:
            print(f"\nNo valid records found in {filename}")
            return 0
        
        file_records = len(records)
        total_records += file_records
        print(f"\nFound {file_records} valid records in {filename}")
        
       #Seguimiento del progreso de la configuración
        progress = ProgressTracker(file_records)
        
        
        # Convertir registros en objetos variantes
        print("Converting records to variants...")
        variants = []
        for record in records:
            variants.append(Variant(record))
            progress.update()
        
        
        # Insertar variantes en lotes
        print("\nInserting variants into MongoDB...")
        inserted_count = db_ops.insert_batch(variants)
        print(f"Inserted {inserted_count} variants from {filename}")
        
        return inserted_count

    except Exception as e:
        print(f"\nAn error occurred while processing {filename}: {str(e)}")
        return 0
    finally:
        db_ops.close()

def process_vcf_files(filenames):
    total_records = 0
    
    start_time = time.time()  # Start time measurement
    
    with ThreadPoolExecutor() as executor:
        # Submit tasks to the executor
        future_to_file = {executor.submit(process_single_vcf_file, filename): filename for filename in filenames}
        
        for future in as_completed(future_to_file):
            filename = future_to_file[future]
            try:
                result = future.result()
                total_records += result
                print(f"Completed processing {filename} with {result} records inserted.")
            except Exception as e:
                print(f"{filename} generated an exception: {str(e)}")
    
    end_time = time.time()  # End time measurement
    elapsed_time = end_time - start_time  # Calculate elapsed time
    
    print(f"\nAll operations completed successfully:")
    print(f"- Total processed files: {len(filenames)}")
    print(f"- Total records inserted: {total_records}")
    print(f"- Total time taken: {elapsed_time:.2f} seconds")  # Print elapsed time

