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
    """
    Télécharge une vidéo YouTube en MP4.
    GET /youtube/download?url=...&audio_only=0/1
    """
    url = request.args.get("url")
    format = request.args.get("format", "video")  # video ou audio
    quality = request.args.get("quality", "highest")  # highest, 720p, 480p, 360p
    
    if not url:
        return jsonify({"error": "Paramètre 'url' manquant"}), 400

    temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp_youtube')
    ensure_dir(temp_dir)
    temp_filename = f"{uuid.uuid4()}"

    ydl_opts = {
        "outtmpl": os.path.join(temp_dir, f"{temp_filename}.%(ext)s"),
        "format": "bestaudio/best" if format == "audio" else get_format_string(quality),
        "postprocessors": [],
        "ignoreerrors": True,
        "no_warnings": True,
        "extract_flat": False,
        "quiet": True,
        "nocheckcertificate": True,
        "noplaylist": True,
    }

    # Configuration audio si nécessaire
    if format == "audio":
        ydl_opts["postprocessors"].append({
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192"
        })

    try:
        with YoutubeDL(ydl_opts) as ydl:
            # Extraire les informations et le titre de la vidéo
            info = ydl.extract_info(url, download=False)
            if info is None:
                return jsonify({"error": "Impossible d'obtenir les informations de la vidéo"}), 400

            # Créer un nom de fichier sécurisé
            safe_title = secure_filename(info.get('title', 'video'))
            output_ext = 'mp3' if format == 'audio' else 'mp4'
            final_filename = f"{safe_title}.{output_ext}"

            # Télécharger la vidéo
            ydl.download([url])

            # Trouver le fichier téléchargé
            downloaded_file = None
            for file in os.listdir(temp_dir):
                if file.startswith(temp_filename):
                    downloaded_file = os.path.join(temp_dir, file)
                    break

            if not downloaded_file or not os.path.exists(downloaded_file):
                raise Exception("Le fichier téléchargé est introuvable")

            try:
                return send_file(
                    downloaded_file,
                    as_attachment=True,
                    download_name=final_filename,
                    mimetype='audio/mpeg' if format == 'audio' else 'video/mp4'
                )
            finally:
                # Nettoyage différé du fichier temporaire
                @after_this_request
                def remove_file(response):
                    try:
                        if os.path.exists(downloaded_file):
                            os.remove(downloaded_file)
                    except Exception as e:
                        current_app.logger.error(f"Erreur lors de la suppression du fichier temporaire: {e}")
                    return response

    except Exception as e:
        error_msg = str(e)
        if "Unable to extract uploader id" in error_msg:
            return jsonify({"error": "La vidéo n'est pas accessible. Elle est peut-être privée ou a été supprimée."}), 400
        return jsonify({"error": f"Erreur : {error_msg}"}), 500

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