import asyncio
import logging
import os
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

import nest_asyncio
from bson import ObjectId
from flask import Flask, jsonify, render_template, request
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient

from app.login.login import search_user
from config.db_config import MONGODB_CONFIG
from database.db_operations import VariantDBOperations
from procesarData import process_vcf_files  # Import your processing function

nest_asyncio.apply()

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

@app.route('/show_login', methods=['GET'])
def login_page():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        # Guardar el email y la contraseña en variables de entorno temporales
        os.environ['RECIPIENT_EMAIL'] = email
        os.environ['RECIPIENT_PASSWORD'] = password
        
        # Ejecutar la función asíncrona search_user
        user = search_user()
        
        try:
            if user == "Usuario encontrado":
                return render_template('variants_table.html')
            else:
                return render_template('login.html', error=True)
        except Exception as e:
            return f"Error al ejecutar el script: {e}", 500

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

@app.route('/search_variants', methods=['GET'])
def search_variants():
    # Obtener parámetros de búsqueda y paginación desde la URL
    query_params = request.args.to_dict()
    page = int(query_params.pop('page', 1))
    per_page = int(query_params.pop('per_page', 100))

    # Consultar la base de datos de manera paralela
    future = executor.submit(db_operations.search_variants, query_params, page, per_page)
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


if __name__ == '__main__':
    app.run(debug=True)
    