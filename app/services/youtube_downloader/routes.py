from flask import Blueprint, request, send_file, jsonify, render_template, current_app, after_this_request
import os
import uuid
import ffmpeg
from werkzeug.utils import secure_filename
from app.services.common.utils import ensure_dir
from yt_dlp import YoutubeDL

youtube_bp = Blueprint("youtube", __name__)

@youtube_bp.route("/")
def index():
    return render_template('youtube.html')

def get_format_string(quality: str) -> str:
    """Helper pour obtenir le format string selon la qualité"""
    # Format plus précis pour une meilleure qualité
    formats = {
        'highest': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '1080p': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]',
        '720p': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]',
        '480p': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]',
        '360p': 'bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]'
    }
    return formats.get(quality, formats['highest'])

def create_ydl_opts(format_type: str, quality: str, output_path: str, ffmpeg_path: str) -> dict:
    """Crée les options yt-dlp optimisées"""
    ydl_opts = {
        "outtmpl": output_path,
        "format": "bestaudio/best" if format_type == "audio" else get_format_string(quality),
        "ffmpeg_location": ffmpeg_path,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "progress_hooks": [],
        "postprocessor_hooks": [],
        "merge_output_format": "mp4"
    }

    if format_type == "audio":
        ydl_opts.update({
            "postprocessors": [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                'nopostoverwrites': False,
            }],
            "format": "bestaudio/best",
            "extractaudio": True
        })
    else:
        ydl_opts.update({
            "postprocessors": [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }]
        })

    return ydl_opts

@youtube_bp.route("/download", methods=["GET"])
def download_youtube_video():
    url = request.args.get("url")
    format = request.args.get("format", "video")
    quality = request.args.get("quality", "highest")
    
    if not url:
        return jsonify({"error": "URL manquante"}), 400

    try:
        ydl_opts = {
            "outtmpl": os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_youtube', f"{uuid.uuid4()}.%(ext)s"),
            "format": "bestaudio/best" if format == "audio" else get_format_string(quality),
            "postprocessors": [],
            "quiet": True,
            "noplaylist": True
        }

        if format == "audio":
            ydl_opts["postprocessors"].append({
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192"
            })

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            if not info:
                return jsonify({"error": "Impossible d'obtenir les informations de la vidéo"}), 400

            downloaded_file = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_youtube', 
                                         f"{info['id']}.{info.get('ext', 'mp4')}")
            
            response = send_file(downloaded_file, as_attachment=True, 
                               download_name=f"{secure_filename(info['title'])}.{info.get('ext', 'mp4')}")

            @after_this_request
            def cleanup(response):
                safe_remove_file(downloaded_file)
                return response

            return response

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@youtube_bp.route("/info", methods=["GET"])
def get_video_info():
    """
    Obtient les informations d'une vidéo YouTube.
    GET /youtube/info?url=...
    """
    url = request.args.get("url")
    
    if not url:
        return jsonify({"error": "Paramètre 'url' manquant"}), 400

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return jsonify({"error": "Impossible d'obtenir les informations de la vidéo"}), 400

            # Formater les informations utiles
            video_info = {
                "title": info.get("title"),
                "duration": info.get("duration"),
                "thumbnail": info.get("thumbnail"),
                "channel": info.get("uploader"),
                "views": info.get("view_count"),
                "description": info.get("description"),
                "formats": []
            }

            # Ajouter les formats disponibles
            if "formats" in info:
                for f in info["formats"]:
                    if f.get("height"):  # Ne garder que les formats vidéo avec une résolution
                        video_info["formats"].append({
                            "format_id": f.get("format_id"),
                            "ext": f.get("ext"),
                            "resolution": f"{f.get('height', '')}p",
                            "filesize": f.get("filesize"),
                            "vcodec": f.get("vcodec"),
                            "acodec": f.get("acodec")
                        })

            return jsonify(video_info)

    except Exception as e:
        error_msg = str(e)
        if "Unable to extract uploader id" in error_msg:
            return jsonify({"error": "La vidéo n'est pas accessible"}), 400
        return jsonify({"error": f"Erreur : {error_msg}"}), 500

def safe_remove_file(filepath):
    """Supprime un fichier en toute sécurité"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la suppression de {filepath}: {str(e)}")

@youtube_bp.route('/download', methods=['POST'])
def download_video():
    ffmpeg_path = current_app.config.get('FFMPEG_PATH')
    if not ffmpeg_path or not os.path.exists(ffmpeg_path):
        return jsonify({"error": "FFmpeg non trouvé"}), 500

    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL manquante"}), 400

    temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_youtube')
    ensure_dir(temp_dir)
    
    try:
        format_type = data.get('format', 'video')
        quality = data.get('quality', 'highest')
        output_template = os.path.join(temp_dir, f"{uuid.uuid4()}.%(ext)s")
        
        ydl_opts = create_ydl_opts(format_type, quality, output_template, ffmpeg_path)
        
        with YoutubeDL(ydl_opts) as ydl:
            # Téléchargement et conversion
            info = ydl.extract_info(data['url'], download=True)
            if not info:
                return jsonify({"error": "Impossible d'obtenir la vidéo"}), 400

            # Détermination du fichier de sortie
            output_file = ydl.prepare_filename(info)
            if format_type == "audio":
                base = os.path.splitext(output_file)[0]
                output_file = f"{base}.mp3"

            if not os.path.exists(output_file):
                return jsonify({"error": "Fichier de sortie non trouvé"}), 500

            return send_file(
                output_file,
                as_attachment=True,
                download_name=f"{secure_filename(info['title'])}.{'mp3' if format_type == 'audio' else 'mp4'}"
            )

    except Exception as e:
        current_app.logger.error(f"Erreur de téléchargement: {str(e)}")
        return jsonify({"error": str(e)}), 500

    finally:
        # Nettoyage des fichiers temporaires
        for f in os.listdir(temp_dir):
            safe_remove_file(os.path.join(temp_dir, f))