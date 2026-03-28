import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import smtplib
from email.message import EmailMessage
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for local development

# Configuration
SMTP_EMAIL = os.getenv("SMTP_EMAIL", "mppraveen110@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
ADMIN_RECEIVER = "mppraveen110@gmail.com"

@app.route('/')
def index():
    """Serve the main portfolio page."""
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve other static files (images, css, etc.)."""
    return send_from_directory('.', path)

@app.route('/api/contact', methods=['POST'])
def api_contact():
    """Handle contact form submissions."""
    try:
        data = request.get_json() or {}
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        subject = data.get('subject', 'No Subject').strip()
        message = data.get('message', '').strip()

        if not name or not email or not message:
            return jsonify({"success": False, "error": "Name, Email, and Message are required."}), 400

        if not SMTP_PASSWORD:
            print(f"⚠️ SMTP password not found in .env. Message from {name} ({email}) discarded.")
            return jsonify({"success": False, "error": "Email delivery is currently disabled. Admin has not set up SMTP credentials."}), 503

        # Prepare Email
        msg = EmailMessage()
        msg['Subject'] = f"Portfolio Contact: {subject}"
        msg['From'] = SMTP_EMAIL
        msg['To'] = ADMIN_RECEIVER
        msg['Reply-To'] = email
        msg.set_content(f"You have a new message from your portfolio!\n\nName: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}\n\nSent at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        # Send Email
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)
            print(f"✅ Contact message from {name} sent to {ADMIN_RECEIVER}.")

        return jsonify({"success": True, "message": "Your message has been sent successfully! ✨"})

    except Exception as e:
        err_str = str(e)
        print(f"❌ Contact Email Error: {e}")
        if "535" in err_str:
             return jsonify({
                 "success": False, 
                 "error": "Authentication Failed. Please ensure you are using a 16-character 'App Password' from Google, not your regular password."
             }), 401
        return jsonify({"success": False, "error": f"Failed to send message: {err_str}"}), 500

if __name__ == '__main__':
    print(f"🚀 Portfolio Server running at http://localhost:5000")
    app.run(port=5000, debug=True)
