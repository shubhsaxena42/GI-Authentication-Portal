"""
main.py — Single entry point for the GI Verification Portal.
Run this file directly. It will:
  1. Auto-detect your local network IP.
  2. Regenerate the QR code for all existing records in database.xlsx.
  3. Start the Flask server on port 5000.
"""

import os
import sys
import socket
import subprocess

def get_local_ip():
    """Get the machine's LAN IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'

def ensure_dependencies():
    """Install requirements if not already installed."""
    try:
        import flask, pandas, qrcode, openpyxl
        print("[OK] All dependencies are installed.")
    except ImportError:
        print("[SETUP] Installing required packages...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        print("[OK] Dependencies installed successfully.")

def generate_qr_codes(base_url):
    """Generate/refresh QR codes for all records in database.xlsx."""
    import pandas as pd
    import qrcode as qrcode_lib

    QR_DIR = 'qrcodes'
    DB_FILE = 'database.xlsx'

    if not os.path.exists(QR_DIR):
        os.makedirs(QR_DIR)

    if not os.path.exists(DB_FILE):
        print(f"[WARN] {DB_FILE} not found. QR codes will be generated on first registration.")
        return

    df = pd.read_excel(DB_FILE, dtype=str)

    if 'Application Number' not in df.columns:
        print("[WARN] 'Application Number' column not found in database. Skipping QR generation.")
        return

    count = 0
    for _, row in df.iterrows():
        app_num = str(row.get('Application Number', '')).strip()
        if not app_num or app_num == 'nan':
            continue

        url = f"{base_url}/?id={app_num}"
        qr = qrcode_lib.QRCode(version=1, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        qr_path = os.path.join(QR_DIR, f"{app_num}_qrcode.png")
        img.save(qr_path)
        count += 1
        print(f"  [QR] Created: {qr_path}  →  {url}")

    print(f"[OK] {count} QR code(s) generated/refreshed in '{QR_DIR}/'")

if __name__ == '__main__':
    print("=" * 60)
    print("  GI Verification Portal — Starting Up")
    print("=" * 60)

    # Step 1: Check dependencies
    ensure_dependencies()

    # Step 2: Set URL for QR Generation
    # Use Production URL so QR codes work after deployment
    production_url = "https://gi-authentication-portal-git-main-shubhsaxena42s-projects.vercel.app"
    print(f"\n[NET] Production URL for QR: {production_url}")

    # Step 3: Generate/refresh QR codes
    print("\n[QR] Refreshing QR codes...")
    generate_qr_codes(production_url)

    # Step 4: Start Flask server
    print(f"\n[SERVER] Starting Flask server...")
    print(f"  ➜ Local:      http://127.0.0.1:5000")
    print(f"  ➜ Production: {production_url}")
    print(f"  ➜ Test Live:  {production_url}/?id=654")
    print("\n  Scan the QR from 'qrcodes/' folder using your phone.")
    print("  Press Ctrl+C to stop the server.\n")
    print("=" * 60)

    # Import and run the Flask app
    from app import app
    app.run(host='0.0.0.0', debug=False, port=5000)
