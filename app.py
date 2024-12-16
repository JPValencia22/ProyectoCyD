import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
from bson import ObjectId
from flask import Flask, request, jsonify
import os
from config.db_config import MONGODB_CONFIG
from procesarData import process_vcf_files  # Import your processing function
from database.db_operations import VariantDBOperations
from pymongo import MongoClient
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
import nest_asyncio
nest_asyncio.apply()
from flask import render_template
import logging
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



@app.route('/')
def home():
    return render_template('home.html')


@app.route('/upload', methods=['GET'])
def upload_page():
    return render_template('upload.html')

@app.route('/show_register', methods=['GET'])
def show_register():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.form.get('email')   
    password = request.form.get('password')

    # Aquí puedes agregar la lógica para registrar al usuario, como guardar en la base de datos
    return jsonify({"message": "User  registered successfully!"}), 201

@app.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Endpoint to process uploaded VCF files."""
    vcf_files = []

    # Check if files were uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    files = request.files.getlist('file')  # Get the list of uploaded files

    for file in files:
        if file and file.filename.endswith('.vcf'):
            # Save the file to a temporary location
            temp_file_path = os.path.join('uploads', file.filename)
            os.makedirs('uploads', exist_ok=True)  # Ensure the uploads directory exists
            file.save(temp_file_path)  # Save the uploaded file
            vcf_files.append(temp_file_path)
        else:
            return jsonify({'error': 'Invalid file type. Only VCF files are allowed.'}), 400

    # Process the VCF files
    process_vcf_files(vcf_files)  # Call your processing function

    try:
        shutil.rmtree('uploads')  # Remove the uploads directory and all its contents
        print("Temporary upload folder removed successfully.")
    except Exception as e:
        print(f"Error removing temporary upload folder: {str(e)}")

    return jsonify({'message': 'Files processed successfully'}), 200


# ThreadPoolExecutor global
executor = ThreadPoolExecutor(max_workers=os.cpu_count() * 8)

# Configuración de cliente asincrónico
client = AsyncIOMotorClient(host=MONGODB_CONFIG['host'], port=MONGODB_CONFIG['port'])
db = client[MONGODB_CONFIG['database']]
collection = db[MONGODB_CONFIG['collection']]

def convert_objectid(doc):
    """ Convierte ObjectId a string en documentos de MongoDB """
    if '_id' in doc and isinstance(doc['_id'], ObjectId):
        doc['_id'] = str(doc['_id'])
    return doc

async def fetch_batch(skip, limit, projection):
    try:
        print(f"Fetching batch with skip={skip}, limit={limit}, projection={projection}")
        
        cursor = collection.find({}, projection).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)

        print(f"Documents retrieved: {len(documents)}")
        
        if not documents:
            print("No documents found for the given skip and limit.")

        return [convert_objectid(doc) for doc in documents]
    except Exception as e:
        print(f"Error in fetch_batch: {str(e)}")
        return []
    
async def get_all_variants_async():
    try:
        total_documents = await collection.estimated_document_count()
        batch_size = max(10000, total_documents // (os.cpu_count() * 4))
        projection = {'_id': 1}  # Solo devolver campos necesarios

        tasks = [fetch_batch(skip, batch_size, projection) for skip in range(0, total_documents, batch_size)]

        results = await asyncio.gather(*tasks, return_exceptions=True)
        variants = [doc for result in results if isinstance(result, list) for doc in result]
        return {'variants': variants}
    except Exception as e:
        return {'error': str(e)}

@app.route('/all_variants', methods=['GET'])
async def get_all_variants():
    try:
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 100))  # Set default limit to 1000

        # Optional: Set a maximum limit to prevent excessive data retrieval
        if limit > 500000:
            return jsonify({'error': 'El límite no puede exceder 50,000 documentos'}), 400

        # Obtener el total de variantes en la base de datos
        total_variants = await collection.estimated_document_count()
        logging.info(f'Total variants in the database: {total_variants}')  # Log the total count

        # Llamar a la función asíncrona para obtener los documentos
        result = await fetch_batch(skip, limit, None)

        # Log the number of variants retrieved for the current request
        logging.info(f'GET /all_variants: Retrieved {len(result)} variants from the database.')  # Log the count of retrieved variants

        # Verificar si el resultado está vacío o no tiene la estructura esperada
        if not result or not isinstance(result, list):
            logging.warning("Result is empty or not a list.")
            return render_template('variants_table.html', variants=[], skip=skip, limit=limit)

        # Renderizar la tabla con todos los datos
        return render_template('variants_table.html', variants=result, skip=skip, limit=limit)
    except Exception as e:
        logging.error(f"Error in get_all_variants: {str(e)}")  # Log the error
        return jsonify({'error': str(e)}), 500

async def search_variants(search_term, skip, limit):
    try:
        query = {
            '$text': {'$search': search_term}
        }
        cursor = collection.find(query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        return [convert_objectid(doc) for doc in documents]
    except Exception as e:
        print(f"Error in search_variants: {e}")
        return []

@app.route('/search_variants', methods=['GET'])
async def search_variants():
    try:
        query = request.args.get('query', '').strip()
        skip = int(request.args.get('skip', 0))
        limit = int(request.args.get('limit', 50))  # Límite máximo para optimizar

        if not query:
            return jsonify({"error": "Se requiere un término de búsqueda"}), 400

        # Optimización: búsqueda utilizando índices y regex insensible a mayúsculas
        search_query = {
            "$or": [
                {"chromosome": {"$regex": query, "$options": "i"}},
                {"variant_id": {"$regex": query, "$options": "i"}},
                {"reference": {"$regex": query, "$options": "i"}},
                {"alternative": {"$regex": query, "$options": "i"}},
                {"info": {"$regex": query, "$options": "i"}}
            ]
        }

        # Obtener resultados de forma asíncrona
        cursor = collection.find(search_query).skip(skip).limit(limit)
        results = await cursor.to_list(length=limit)

        variants = [convert_objectid(doc) for doc in results]

        return jsonify({"variants": variants, "skip": skip, "limit": limit})
    except Exception as e:
        print(f"Error en search_variants: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)