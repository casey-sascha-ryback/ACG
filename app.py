"""
Cybersecurity Toolkit - Main Application File

This file follows the MVC (Model-View-Controller) architecture:
- Models: Located in the tools/ directory (business logic)
- Views: Located in the templates/ directory (UI presentation)
- Controllers: Route handlers in this file (request processing)

This structure makes the application portable to run on any IDE.
"""

import os
import logging
import hashlib
from flask import Flask, render_template, request, jsonify, session
from flask_session import Session

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "cybersecurity-toolkit-secret")

# Configure session to use filesystem
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_USE_SIGNER"] = True
Session(app)

# Import models
from tools.password_analyzer import analyze_password, load_password_model
from models.leakcheck_integration import check_breach
from tools.file_integrity import calculate_checksum, verify_checksum
from tools.encryption_tool import encrypt_text, decrypt_text, available_algorithms

# Initialize password model
load_password_model()

# Main routes (Controller functions)
@app.route('/')
def index():
    """Home page with overview of the cybersecurity toolkit"""
    return render_template('index.html')

@app.route('/about')
def about():
    """About page with information about the toolkit"""
    return render_template('about.html')

# Password Analyzer routes
@app.route('/password-analyzer')
def password_analyzer():
    """Password strength analyzer page"""
    return render_template('password_analyzer.html')

@app.route('/api/analyze-password', methods=['POST'])
def api_analyze_password():
    """API endpoint to analyze password strength"""
    password = request.form.get('password', '')
    
    if not password:
        return jsonify({
            'error': 'No password provided',
            'strength': 0,
            'feedback': ['Please enter a password']
        })
    
    result = analyze_password(password)
    return jsonify(result)

# Dark Web Monitor routes
@app.route('/dark-web-monitor')
def dark_web_monitor():
    """Dark web breach monitoring page"""
    return render_template('dark_web_monitor.html')

@app.route('/api/check-breaches', methods=['POST'])
def api_check_breaches():
    """API endpoint to check for breaches using LeakCheck API"""
    email = request.form.get('email', '')
    
    if not email:
        return jsonify({
            'error': 'No email provided',
            'breaches': []
        })
    
    try:
        breaches = check_breach(email)
        return jsonify({
            'breaches': breaches
        })
    except Exception as e:
        logging.error(f"Error checking breaches: {str(e)}")
        return jsonify({
            'error': 'Error checking breaches',
            'message': str(e)
        }), 500

# File Integrity Checker routes
@app.route('/file-integrity')
def file_integrity():
    """File integrity checker page"""
    return render_template('file_integrity.html')

@app.route('/api/calculate-checksum', methods=['POST'])
def api_calculate_checksum():
    """API endpoint to calculate file checksum"""
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    algorithm = request.form.get('algorithm', 'sha256')
    
    if file.filename == '':
        return jsonify({
            'error': 'No file selected'
        }), 400
    
    try:
        checksum = calculate_checksum(file, algorithm)
        return jsonify({
            'filename': file.filename,
            'algorithm': algorithm,
            'checksum': checksum
        })
    except Exception as e:
        logging.error(f"Error calculating checksum: {str(e)}")
        return jsonify({
            'error': 'Error calculating checksum',
            'message': str(e)
        }), 500

@app.route('/api/verify-checksum', methods=['POST'])
def api_verify_checksum():
    """API endpoint to verify file checksum"""
    if 'file' not in request.files:
        return jsonify({
            'error': 'No file provided'
        }), 400
    
    file = request.files['file']
    provided_checksum = request.form.get('checksum', '')
    algorithm = request.form.get('algorithm', 'sha256')
    
    if file.filename == '':
        return jsonify({
            'error': 'No file selected'
        }), 400
    
    if not provided_checksum:
        return jsonify({
            'error': 'No checksum provided'
        }), 400
    
    try:
        is_valid, calculated_checksum = verify_checksum(file, provided_checksum, algorithm)
        return jsonify({
            'filename': file.filename,
            'is_valid': is_valid,
            'provided_checksum': provided_checksum,
            'calculated_checksum': calculated_checksum
        })
    except Exception as e:
        logging.error(f"Error verifying checksum: {str(e)}")
        return jsonify({
            'error': 'Error verifying checksum',
            'message': str(e)
        }), 500

# Encryption Tool routes
@app.route('/encryption-tool')
def encryption_tool():
    """Encryption and decryption tool page"""
    algorithms = available_algorithms()
    return render_template('encryption_tool.html', algorithms=algorithms)

@app.route('/api/encrypt', methods=['POST'])
def api_encrypt():
    """API endpoint for encrypting text"""
    text = request.form.get('text', '')
    algorithm = request.form.get('algorithm', 'aes')
    password = request.form.get('password', '')
    
    if not text:
        return jsonify({
            'error': 'No text provided'
        }), 400
    
    if not password:
        return jsonify({
            'error': 'No password provided'
        }), 400
    
    try:
        encrypted_data, salt = encrypt_text(text, password, algorithm)
        return jsonify({
            'encrypted': encrypted_data,
            'salt': salt,
            'algorithm': algorithm
        })
    except Exception as e:
        logging.error(f"Error encrypting text: {str(e)}")
        return jsonify({
            'error': 'Error encrypting text',
            'message': str(e)
        }), 500

@app.route('/api/decrypt', methods=['POST'])
def api_decrypt():
    """API endpoint for decrypting text"""
    encrypted_data = request.form.get('encrypted', '')
    salt = request.form.get('salt', '')
    algorithm = request.form.get('algorithm', 'aes')
    password = request.form.get('password', '')
    
    if not encrypted_data:
        return jsonify({
            'error': 'No encrypted data provided'
        }), 400
    
    if not salt:
        return jsonify({
            'error': 'No salt provided'
        }), 400
    
    if not password:
        return jsonify({
            'error': 'No password provided'
        }), 400
    
    try:
        decrypted_text = decrypt_text(encrypted_data, salt, password, algorithm)
        return jsonify({
            'decrypted': decrypted_text
        })
    except Exception as e:
        logging.error(f"Error decrypting text: {str(e)}")
        return jsonify({
            'error': 'Error decrypting text',
            'message': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# For WSGI servers like Gunicorn
application = app

# Start the app if run directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)