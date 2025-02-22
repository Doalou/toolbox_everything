from flask import Blueprint, render_template, request, jsonify, send_file
from .tools import (generate_password, validate_password, calculate_hash,
                   encode_decode_base64, format_json, minify_code)
from PIL import Image
import io

essentials_bp = Blueprint('essentials', __name__)

@essentials_bp.route('/')
def index():
    return render_template('essentials.html')

@essentials_bp.route('/generate-password', methods=['POST'])
def generate_pwd():
    length = request.json.get('length', 12)
    include_numbers = request.json.get('numbers', True)
    include_symbols = request.json.get('symbols', True)
    
    try:
        password = generate_password(length, include_numbers, include_symbols)
        return jsonify({'password': password})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@essentials_bp.route('/validate-password', methods=['POST'])
def validate_pwd():
    password = request.json.get('password', '')
    return jsonify(validate_password(password))

@essentials_bp.route('/calculate-hash', methods=['POST'])
def calc_hash():
    text = request.json.get('text', '')
    algorithm = request.json.get('algorithm', 'sha256')
    try:
        result = calculate_hash(text, algorithm)
        return jsonify({'hash': result})
    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@essentials_bp.route('/base64', methods=['POST'])
def base64_convert():
    text = request.json.get('text', '')
    operation = request.json.get('operation', 'encode')
    try:
        result = encode_decode_base64(text, operation)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@essentials_bp.route('/format-json', methods=['POST'])
def format_json_data():
    try:
        json_str = request.json.get('json', '')
        indent = request.json.get('indent', 2)
        formatted = format_json(json_str, indent)
        return jsonify({'formatted': formatted})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@essentials_bp.route('/minify', methods=['POST'])
def minify():
    code = request.json.get('code', '')
    language = request.json.get('language', 'json')
    try:
        result = minify_code(code, language)
        return jsonify({'minified': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@essentials_bp.route('/upscale-image', methods=['POST'])
def upscale_image():
    if 'image' not in request.files:
        return jsonify({'error': 'Aucune image fournie'}), 400
        
    file = request.files['image']
    if not file.filename:
        return jsonify({'error': 'Nom de fichier invalide'}), 400
        
    try:
        # Récupération des paramètres
        width = request.form.get('width', type=int)
        height = request.form.get('height', type=int)
        maintain_ratio = request.form.get('maintain_ratio', type=bool, default=True)
        
        # Ouverture et traitement de l'image
        img = Image.open(file.stream)
        
        if maintain_ratio:
            # Calcul des dimensions en conservant le ratio
            ratio = img.width / img.height
            if width:
                height = int(width / ratio)
            elif height:
                width = int(height * ratio)
                
        if width and height:
            img = img.resize((width, height), Image.Resampling.LANCZOS)
        
        # Conversion en bytes
        output = io.BytesIO()
        img.save(output, format=img.format or 'PNG')
        output.seek(0)
        
        return send_file(
            output,
            mimetype=f'image/{img.format.lower() if img.format else "png"}',
            as_attachment=True,
            download_name=f'upscaled_{file.filename}'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
