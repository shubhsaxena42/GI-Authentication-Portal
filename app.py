import os
import io
import base64
import pandas as pd
import qrcode
from flask import Flask, request, jsonify, send_file, send_from_directory
from datetime import datetime

app = Flask(__name__)

# Constants
DB_FILE = 'database.xlsx'
PRODUCTION_URL = 'https://gi-authentication-portal-git-main-shubhsaxena42s-projects.vercel.app'

def load_db():
    try:
        if os.path.exists(DB_FILE):
            return pd.read_excel(DB_FILE, dtype=str)
        # Fallback columns if file is missing in the serverless environment
        return pd.DataFrame(columns=[
            'Application Number', 'Product Name', 'Manufacturer Name',
            'Geographical Indications', 'Status', 'Serial Number',
            'Batch Number', 'Manufacturing Date', 'Expiry Date',
            'Applicant Name', 'Applicant Address', 'Date of Filing',
            'Class', 'Goods', 'Geographical Area', 'Priority Country',
            'Journal Number', 'Availability Date', 'Certificate Number',
            'Certificate Date', 'Registration Valid Upto'
        ])
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return pd.DataFrame()

# Serving Static Files
@app.route('/')
def serve_index():
    return send_file('index.html')

@app.route('/styles.css')
def serve_styles():
    return send_file('styles.css')

@app.route('/product_image.png')
def serve_product_image():
    return send_from_directory('.', 'product_image.png')

@app.route('/iit-logo.png')
def serve_logo():
    return send_from_directory('.', 'iit-logo.png')

@app.route('/gi_image.jpeg')
def serve_gi_image():
    return send_from_directory('.', 'gi_image.jpeg')

@app.route('/api/verify', methods=['GET'])
def verify_product():
    reg_id = request.args.get('id')
    if not reg_id:
        return jsonify({'error': 'Registration ID is required'}), 400

    df = load_db()
    if df.empty:
        return jsonify({'error': 'Database is empty or missing'}), 500

    record = df[df['Application Number'].astype(str) == str(reg_id)]
    
    if not record.empty:
        data = record.iloc[0]
        return jsonify({
            'application_number': str(data.get('Application Number', '')).strip(),
            'product_name': str(data.get('Product Name', '')).strip(),
            'manufacturer_name': str(data.get('Manufacturer Name', '')).strip(),
            'gi_name': str(data.get('Geographical Indications', '')).strip(),
            'status': str(data.get('Status', '')).strip(),
            'serial_number': str(data.get('Serial Number', '')).strip(),
            'batch_number': str(data.get('Batch Number', '')).strip(),
            'mfg_date': str(data.get('Manufacturing Date', '')).strip(),
            'expiry_date': str(data.get('Expiry Date', '')).strip(),
            'applicant_name': str(data.get('Applicant Name', '')).strip(),
            'applicant_address': str(data.get('Applicant Address', '')).strip(),
            'date_of_filing': str(data.get('Date of Filing', '')).strip(),
            'class_num': str(data.get('Class', '')).strip(),
            'goods': str(data.get('Goods', '')).strip(),
            'geographical_area': str(data.get('Geographical Area', '')).strip(),
            'certificate_number': str(data.get('Certificate Number', '')).strip(),
            'certificate_date': str(data.get('Certificate Date', '')).strip(),
            'valid_upto': str(data.get('Registration Valid Upto', '')).strip()
        })
    else:
        return jsonify({'error': 'Product not found. Potential counterfeit.'}), 404

@app.route('/api/register', methods=['POST'])
def register_product():
    data = request.json
    if not data or 'Application Number' not in data:
        return jsonify({'error': 'Invalid data. Application Number is required.'}), 400

    reg_id = str(data['Application Number'])
    
    # Generate QR Code in MEMORY (Base64)
    # Use Production URL for QR codes so they work after deployment
    verification_url = f"{PRODUCTION_URL}/?id={reg_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    
    img_base64 = base64.b64encode(img_io.getvalue()).decode('utf-8')

    # NOTE: Registration will NOT be permanent on Vercel as it is read-only.
    return jsonify({
        'message': 'Registration processed (Memory Only)',
        'qr_code_base64': f"data:image/png;base64,{img_base64}"
    }), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
