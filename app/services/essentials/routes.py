from flask import Blueprint, render_template, request, jsonify, send_file, current_app
from .tools import (PasswordGenerator, analyze_password_strength, calculate_hash,
                   encode_decode_base64, format_json, minify_code, generate_qr, add_logo_to_qr)
from PIL import Image
import io
import json
from werkzeug.utils import secure_filename
import os
from functools import wraps

essentials_bp = Blueprint('essentials', __name__)

def handle_errors(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({'error': str(e)}), 400 if isinstance(e, ValueError) else 500
    return wrapper

def send_file_response(buffer, mimetype, filename):
    """Helper pour envoyer des fichiers"""
    return send_file(
        buffer,
        mimetype=mimetype,
        as_attachment=True,
        download_name=filename
    )

@essentials_bp.route('/')
def index():
    return render_template('essentials.html')

@essentials_bp.route('/generate-password', methods=['POST'])
@handle_errors
def generate_pwd():
    generator = PasswordGenerator()
    config = request.json or {}
    password = generator.configure(**config).generate()
    return jsonify({
        'password': password,
        'analysis': analyze_password_strength(password)
    })

@essentials_bp.route('/validate-password', methods=['POST'])
@handle_errors
def validate_pwd():
    return jsonify(analyze_password_strength(request.json.get('password', '')))

@essentials_bp.route('/calculate-hash', methods=['POST'])
@handle_errors
def calc_hash():
    text = request.json.get('text', '')
    algorithm = request.json.get('algorithm', 'sha256')
    result = calculate_hash(text, algorithm)
    return jsonify({'hash': result})

@essentials_bp.route('/base64', methods=['POST'])
@handle_errors
def base64_convert():
    text = request.json.get('text', '')
    operation = request.json.get('operation', 'encode')
    result = encode_decode_base64(text, operation)
    return jsonify({'result': result})

@essentials_bp.route('/format-json', methods=['POST'])
@handle_errors
def format_json_data():
    json_str = request.json.get('json', '')
    indent = request.json.get('indent', 2)
    formatted = format_json(json_str, indent)
    return jsonify({'formatted': formatted})

@essentials_bp.route('/minify', methods=['POST'])
@handle_errors
def minify():
    code = request.json.get('code', '')
    language = request.json.get('language', 'json')
    result = minify_code(code, language)
    return jsonify({'minified': result})

@essentials_bp.route('/upscale-image', methods=['POST'])
@handle_errors
def upscale_image():
    if 'image' not in request.files:
        raise ValueError('Aucune image fournie')
        
    file = request.files['image']
    if not file.filename:
        raise ValueError('Nom de fichier invalide')
        
    width = request.form.get('width', type=int)
    height = request.form.get('height', type=int)
    maintain_ratio = request.form.get('maintain_ratio', type=bool, default=True)
    
    img = Image.open(file.stream)
    
    if maintain_ratio:
        ratio = img.width / img.height
        if width:
            height = int(width / ratio)
        elif height:
            width = int(height * ratio)
            
    if width and height:
        img = img.resize((width, height), Image.Resampling.LANCZOS)
    
    output = io.BytesIO()
    img.save(output, format=img.format or 'PNG')
    output.seek(0)
    
    return send_file_response(
        output,
        f'image/{img.format.lower() if img.format else "png"}',
        f'upscaled_{file.filename}'
    )

@essentials_bp.route('/generate-qr', methods=['POST'])
@handle_errors
def generate_qr_code():
    data = request.json
    qr_data = data.get('data')
    size = data.get('size', 10)
    border = data.get('border', 4)
    color = tuple(data.get('color', (0, 0, 0)))
    bg_color = tuple(data.get('bg_color', (255, 255, 255)))
    
    if not qr_data:
        raise ValueError('Données manquantes')
        
    buffer = generate_qr(qr_data, size, border, color, bg_color)
    
    return send_file_response(
        buffer,
        'image/png',
        'qrcode.png'
    )

@essentials_bp.route('/add-logo-qr', methods=['POST'])
@handle_errors
def add_logo_to_qr_code():
    if 'qr' not in request.files or 'logo' not in request.files:
        raise ValueError('QR code et logo requis')
        
    qr_file = request.files['qr']
    logo_file = request.files['logo']
    
    logo_filename = secure_filename(logo_file.filename)
    logo_path = os.path.join(current_app.config['TEMP_FOLDER'], logo_filename)
    logo_file.save(logo_path)
    
    try:
        buffer = add_logo_to_qr(qr_file, logo_path)
        
        return send_file_response(
            buffer,
            'image/png',
            'qrcode_with_logo.png'
        )
    finally:
        if os.path.exists(logo_path):
            os.remove(logo_path)

@essentials_bp.route('/calculate-hash-file', methods=['POST'])
@handle_errors
def calc_hash_file():
    if 'file' not in request.files:
        raise ValueError('Aucun fichier fourni')
        
    file = request.files['file']
    if not file.filename:
        raise ValueError('Nom de fichier invalide')
        
    algorithm = request.form.get('algorithm', 'sha256')
    content = file.read()
    
    # Calculer le hash
    hasher = HASH_ALGORITHMS[algorithm]()
    hasher.update(content)
    
    return jsonify({'hash': hasher.hexdigest()})
