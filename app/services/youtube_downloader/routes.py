from flask import Blueprint, request, send_file, jsonify, render_template, current_app, after_this_request
import os
import uuid
from werkzeug.utils import secure_filename
from app.services.common.utils import ensure_dir
from yt_dlp import YoutubeDL

youtube_bp = Blueprint("youtube", __name__)

@youtube_bp.route("/")
def index():
    return render_template('youtube.html')

def get_format_string(quality: str) -> str:
    """Helper pour obtenir le format string selon la qualité"""
    formats = {
        'highest': 'bestvideo+bestaudio/best',
        '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
        '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
        '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]'
    }
    return formats.get(quality, 'bestvideo+bestaudio/best')

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

@youtube_bp.route('/download', methods=['POST'])
def download_video():
    url = request.json.get('url')
    format = request.json.get('format', 'mp4')
    
    if not url:
        return jsonify({'error': 'No URL provided'}), 400
        
    download_path = current_app.config['YOUTUBE_DOWNLOAD_FOLDER']
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
        'max_duration': current_app.config['YOUTUBE_MAX_DURATION']
    }
    
    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            return jsonify({
                'status': 'success',
                'title': info['title'],
                'filename': f"{info['title']}.{info['ext']}"
            })
    except Exception as e:
        current_app.logger.error(f'Error downloading video: {str(e)}')
        return jsonify({'error': str(e)}), 500