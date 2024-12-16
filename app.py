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

    return jsonify({'message': 'Files processed successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)