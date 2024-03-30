from flask import Blueprint, request, send_from_directory, jsonify, render_template
import pdfkit
from werkzeug.utils import secure_filename
import os
from pdfkit import configuration

# Define the Blueprint
html_to_pdf_bp = Blueprint('html_to_pdf', __name__, template_folder='templates')

UPLOAD_FOLDER = 'uploads'
PDF_FOLDER = 'pdfs'

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.exists(PDF_FOLDER):
    os.makedirs(PDF_FOLDER)

# Update the path to wkhtmltopdf according to your system's configuration
WKHTMLTOPDF_PATH = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'

@html_to_pdf_bp.route('/upload', methods=['GET'])
def show_upload_form():
    return render_template('upload_form.html')

@html_to_pdf_bp.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # Secure the filename and validate the file type
    filename = secure_filename(file.filename)
    if not filename.lower().endswith('.html'):
        return jsonify({'error': 'Invalid file type. Please upload an HTML file.'}), 400
    
    html_path = os.path.join(UPLOAD_FOLDER, filename)
    
    # Save the file safely, ensuring directory traversal is not possible
    file.save(html_path)
    
    # Configuration for pdfkit to find wkhtmltopdf
    config = configuration(wkhtmltopdf=WKHTMLTOPDF_PATH)
    
    # Generate a unique PDF filename to prevent overwriting
    pdf_filename = os.path.splitext(filename)[0] + '.pdf'
    pdf_path = os.path.join(PDF_FOLDER, pdf_filename)
    
    try:
        pdfkit.from_file(html_path, pdf_path, configuration=config)
    except Exception as e:
        return jsonify({'error': 'Failed to convert file to PDF.', 'exception': str(e)}), 500
    
    return jsonify({'message': 'File converted successfully', 'pdf_filename': pdf_filename})

@html_to_pdf_bp.route('/pdfs/<path:filename>', methods=['GET'])
def download_pdf(filename):
    # Securely parse the filename to prevent directory traversal
    secure_filename(filename)
    return send_from_directory(directory=PDF_FOLDER, filename=filename, as_attachment=True)
