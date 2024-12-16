import asyncio
from concurrent.futures import ThreadPoolExecutor, as_completed
import shutil
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
import subprocess

app = Flask(__name__)


db_operations = VariantDBOperations()
executor = ThreadPoolExecutor()
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

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        # Guardar el email en una variable de entorno temporal
        os.environ['RECIPIENT_EMAIL'] = email
        try:
            # Ejecutar el script producer.py
            subprocess.run(['python', 'app/email/producer.py'], check=True)
            return render_template('login.html')
        except subprocess.CalledProcessError as e:
            return f"Error al ejecutar el script: {e}", 500

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


@app.route('/variants', methods=['GET'])
def variants_page():
    # Renderiza el template que consume el JSON
    return render_template('variants_table.html')
    
@app.route('/all_variants', methods=['GET'])
def all_variants():
    # Obtener parámetros de paginación desde la URL
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 100))

    # Consultar la base de datos de manera paralela
    future = executor.submit(db_operations.get_paginated_variants, page, per_page)
    variants, total = future.result()

    total_pages = (total + per_page - 1) // per_page 

    # Devolver resultados como JSON para carga dinámica
    return jsonify({
        'variants': variants,
        'total': total,
        'total_pages': total_pages,
        'page': page,
        'per_page': per_page
    })
 


def search_variants(self, query_params, page, per_page):
        skip = (page - 1) * per_page
        search_filters = {}

        # Construir filtros dinámicamente
        if 'Chrom' in query_params:
            search_filters['chromosome'] = query_params['Chrom']
        if 'Filter' in query_params:
            search_filters['filter'] = query_params['Filter']
        if 'Info' in query_params:
            search_filters['$text'] = {'$search': query_params['Info']}
        if 'Format' in query_params:
            search_filters['format'] = query_params['Format']
        
        # Búsqueda paralela con ThreadPoolExecutor
        with ThreadPoolExecutor() as executor:
            future = executor.submit(
                self.collection.find, search_filters, {'_id': 0}
            )
            cursor = future.result().skip(skip).limit(per_page)
            
        variants = list(cursor)
        
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

        total = self.collection.count_documents(search_filters)
        return result, total


if __name__ == '__main__':
    app.run(debug=True)