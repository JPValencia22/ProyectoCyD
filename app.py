from flask import Flask, request, jsonify
import os
from procesarData import process_vcf_files  # Import your processing function

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the VCF Upload API!"})

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