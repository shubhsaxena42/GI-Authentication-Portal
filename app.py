import os
import pandas as pd
import qrcode
from flask import Flask, request, jsonify, send_file, send_from_directory
from datetime import datetime

app = Flask(__name__)

# Constants
DB_FILE = 'database.xlsx'
QR_DIR = 'qrcodes'

# Ensure the QR directory exists
if not os.path.exists(QR_DIR):
    os.makedirs(QR_DIR)

# Initialize the internal database if it doesn't exist
if not os.path.exists(DB_FILE):
    df_initial = pd.DataFrame(columns=[
        'Application Number', 
        'Product Name',
        'Manufacturer Name',
        'Geographical Indications', 
        'Status', 
        'Serial Number',
        'Batch Number',
        'Manufacturing Date',
        'Expiry Date',
        'Applicant Name', 
        'Applicant Address',
        'Date of Filing',
        'Class',
        'Goods',
        'Geographical Area',
        'Priority Country',
        'Journal Number',
        'Availability Date',
        'Certificate Number',
        'Certificate Date',
        'Registration Valid Upto'
    ])
    # Add multiple dummy rows for testing
    df_initial.loc[0] = [
        '654', 
        'Authentic Thulma Blanket',
        'Uttarakhand Handloom Board',
        'Uttarakhand Thulma', 
        'Registered', 
        'SN-2024-001',
        'BATCH-A1',
        '01/01/2024',
        '01/01/2029',
        'Gauri Shankar Nidhi Swayat Sahkarita', 
        'Madcoat, Munasyari, Pithoragarh, Uttarakhand, India', 
        '27/05/2019', 
        '24', 
        'Handi Crafts', 
        'Uttarakhand', 
        'India', 
        '138', 
        '30/06/2020', 
        '393', 
        '14/09/2021', 
        '26/05/2029'
    ]
    df_initial.loc[1] = [
        '655', 
        'Basmati Rice (Dehradun)',
        'Doon valley Farmers',
        'Basmati Rice', 
        'Registered', 
        'SN-2024-B-09',
        'BATCH-RICE-01',
        '15/05/2024',
        '15/05/2026',
        'Heritage Farmers Society', 
        'Dehradun, Uttarakhand, India', 
        '12/03/2018', 
        '30', 
        'Agriculture', 
        'Uttarakhand', 
        'India', 
        '142', 
        '10/10/2019', 
        '401', 
        '20/02/2022', 
        '11/03/2028'
    ]
    df_initial.to_excel(DB_FILE, index=False)

def load_db():
    try:
        if os.path.exists(DB_FILE):
            return pd.read_excel(DB_FILE, dtype=str)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error loading Excel file: {e}")
        return pd.DataFrame()

def save_db(df):
    df.to_excel(DB_FILE, index=False)

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

    # Search for exactly matching Application Number
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
    """
    Endpoint for Google Forms (via App Script webhook) to send new registration data.
    """
    data = request.json
    if not data or 'Application Number' not in data:
        return jsonify({'error': 'Invalid data. Application Number is required.'}), 400

    reg_id = str(data['Application Number'])
    
    df = load_db()
    
    # Check if ID already exists
    if not df.empty and reg_id in df['Application Number'].astype(str).values:
        return jsonify({'error': 'Application Number already exists'}), 400

    new_row_data = {
        'Application Number': reg_id,
        'Geographical Indications': data.get('Geographical Indications', 'Unknown'),
        'Status': data.get('Status', 'Registered'),
        'Applicant Name': data.get('Applicant Name', 'Unknown'),
        'Applicant Address': data.get('Applicant Address', ''),
        'Date of Filing': data.get('Date of Filing', ''),
        'Class': data.get('Class', ''),
        'Goods': data.get('Goods', ''),
        'Geographical Area': data.get('Geographical Area', ''),
        'Priority Country': data.get('Priority Country', 'India'),
        'Journal Number': data.get('Journal Number', ''),
        'Availability Date': data.get('Availability Date', ''),
        'Certificate Number': data.get('Certificate Number', ''),
        'Certificate Date': data.get('Certificate Date', datetime.now().strftime('%d/%m/%Y')),
        'Registration Valid Upto': data.get('Registration Valid Upto', '')
    }
    
    new_row = pd.DataFrame([new_row_data])
    
    df = pd.concat([df, new_row], ignore_index=True)
    save_db(df)

    # Generate QR Code pointing to the verification portal
    # Provide the root URL or deployed URL where scanning a QR goes to ?id=REG_ID
    # Since it's a prototype, use a placeholder domain or localhost
    # You should replace BASE_URL with your Vercel URL later.
    base_url = "https://your-vercel-domain.vercel.app"
    verification_url = f"{base_url}/?id={reg_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(verification_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill='black', back_color='white')
    qr_filename = f"{reg_id}_qrcode.png"
    qr_path = os.path.join(QR_DIR, qr_filename)
    img.save(qr_path)

    return jsonify({
        'message': 'Registration successful',
        'qr_code_file': qr_filename
    }), 201

@app.route('/download/qr/<filename>')
def download_qr(filename):
    """
    Allow downloading the generated QR code.
    """
    return send_from_directory(QR_DIR, filename, as_attachment=True)

if __name__ == '__main__':
    print("Starting Flask server on port 5000...")
    print("Try opening http://localhost:5000 or http://localhost:5000/?id=654")
    app.run(host='0.0.0.0', debug=True, port=5000)
