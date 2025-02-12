from flask import Blueprint, request, jsonify, send_file, render_template, current_app
from PIL import Image
import io
import os
import zipfile
import ffmpeg
import uuid
from werkzeug.utils import secure_filename
from app.services.common.utils import log_message, ensure_dir, create_unique_filename

media_bp = Blueprint("media", __name__)  # Renommé de images_bp à media_bp

@media_bp.route("/")
def index():
    return render_template('media.html')  # Mise à jour du nom du template

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_MEDIA_EXTENSIONS']

def is_video(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_VIDEO_EXTENSIONS']

def process_image(img, output_format, quality=85):
    """Fonction utilitaire pour traiter une image"""
    output = io.BytesIO()
    
    try:
        if output_format == "JPEG":
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            img.save(output, format=output_format, quality=quality, optimize=True)
        else:
            img.save(output, format=output_format, optimize=True)
        
        output.seek(0)
        return output
    except Exception as e:
        raise ValueError(f"Erreur lors du traitement de l'image: {str(e)}")

def process_video(input_path, output_format, quality=85):
    """Fonction pour convertir une vidéo"""
    try:
        # Utiliser un nom de fichier unique basé sur UUID pour éviter les conflits
        unique_filename = str(uuid.uuid4())
        output_path = os.path.join(
            current_app.config['UPLOAD_FOLDER'], 
            'temp', 
            f"{unique_filename}.{output_format}"
        )
        
        # Configuration de la qualité (CRF - Constant Rate Factor)
        crf = int(28 - (quality/100.0 * 10))  # Convertit 1-100 en 28-18
        
        # Configuration codec selon le format de sortie
        codec_config = {
            'mp4': {'c:v': 'libx264', 'crf': str(crf), 'preset': 'medium'},
            'webm': {'c:v': 'libvpx-vp9', 'crf': str(crf), 'b:v': '0'},
            'avi': {'c:v': 'libx264', 'crf': str(crf)},
            'mkv': {'c:v': 'libx264', 'crf': str(crf)}
        }
        
        stream = ffmpeg.input(input_path)
        stream = ffmpeg.output(stream, output_path, **codec_config.get(output_format, {'c:v': 'copy'}))
        ffmpeg.run(stream, overwrite_output=True)
        
        return output_path
    except Exception as e:
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
            except:
                pass
        raise ValueError(f"Erreur lors de la conversion vidéo: {str(e)}")

@media_bp.route("/convert", methods=["POST"])
def convert_media():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No filename provided'}), 400
        
    filename = secure_filename(file.filename)
    target_format = request.form.get('format', 'webp')
    quality = int(request.form.get('quality', current_app.config['DEFAULT_QUALITY']))
    
    temp_dir = ensure_dir(current_app.config['TEMP_FOLDER'])
    temp_path = create_unique_filename(filename, temp_dir)
    
    try:
        file.save(temp_path)
        # Logique de conversion à implémenter
        return jsonify({'status': 'success', 'message': 'File converted successfully'})
    except Exception as e:
        current_app.logger.error(f'Error converting file: {str(e)}')
        return jsonify({'error': str(e)}), 500

@media_bp.route("/batch", methods=["POST"])
def batch_process():
    """Traite plusieurs images en une seule fois"""
    if "files[]" not in request.files:
        return jsonify({"error": "Aucun fichier transmis"}), 400

    files = request.files.getlist("files[]")
    
    # Création d'un ZIP pour les résultats
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w') as zf:
        for file in files:
            if file and allowed_file(file.filename):
                try:
                    img = Image.open(file.stream)
                    output_format = request.form.get("output_format", "JPEG").upper()
                    quality = int(request.form.get("quality", 85))
                    processed = process_image(img, output_format, quality)
                    filename = f"converted_{secure_filename(file.filename)}"
                    zf.writestr(filename, processed.getvalue())
                except Exception as e:
                    current_app.logger.error(f"Erreur sur {file.filename}: {str(e)}")
                    continue

    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='processed_images.zip'
    )
