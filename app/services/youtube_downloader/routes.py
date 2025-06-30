from flask import Blueprint, request, send_file, jsonify, render_template, current_app, after_this_request
import os
import uuid
import subprocess
import shutil
from werkzeug.utils import secure_filename
from app.services.common.utils import ensure_dir
from yt_dlp import YoutubeDL
import re
import unicodedata
import tempfile

youtube_bp = Blueprint("youtube", __name__)

@youtube_bp.route("/")
def index():
    return render_template('youtube.html')

def get_ffmpeg_path():
    """Trouve le chemin vers FFmpeg - Version Docker/Linux optimisée"""
    # Pour l'environnement Docker, FFmpeg est installé dans /usr/bin
    potential_paths = [
        '/usr/bin/ffmpeg',  # Chemin standard Linux/Docker  
        'ffmpeg'  # Fallback dans le PATH
    ]
    
    for path in potential_paths:
        if shutil.which(path) or os.path.isfile(path):
            return path
    
    return None

def verify_ffmpeg():
    """Vérifie que FFmpeg est disponible"""
    ffmpeg_path = get_ffmpeg_path()
    if not ffmpeg_path:
        return False, "FFmpeg n'est pas installé sur ce système"
    
    try:
        result = subprocess.run(
            [ffmpeg_path, '-version'], 
            capture_output=True, 
            text=True, 
            timeout=10
        )
        if result.returncode == 0:
            return True, ffmpeg_path
        else:
            return False, f"FFmpeg trouvé mais non fonctionnel: {result.stderr}"
    except Exception as e:
        return False, f"Erreur lors de la vérification de FFmpeg: {str(e)}"

def get_format_string(quality: str) -> str:
    """
    Génère une chaîne de format robuste pour yt-dlp.
    Version corrigée pour forcer vraiment la meilleure qualité.
    """
    quality_map = {
        # Pour la meilleure qualité : on essaie d'abord les hautes résolutions puis on descend
        'highest': 'best[height>=2160]/best[height>=1440]/best[height>=1080]/best[height>=720]/best',
        # Pour les qualités spécifiques, on utilise une approche plus précise
        '1080p': 'best[height<=1080][height>=1080]/best[height<=1080]',
        '720p': 'best[height<=720][height>=720]/best[height<=720]', 
        '480p': 'best[height<=480][height>=480]/best[height<=480]',
        '360p': 'best[height<=360][height>=360]/best[height<=360]',
    }
    return quality_map.get(quality, 'best[height>=2160]/best[height>=1440]/best[height>=1080]/best')

def sanitize_filename(filename):
    """Nettoie le nom de fichier en supprimant les caractères spéciaux"""
    if not filename:
        return "video"
    
    # Normaliser les caractères Unicode
    filename = unicodedata.normalize('NFKD', filename)
    filename = filename.encode('ASCII', 'ignore').decode('ASCII')
    
    # Supprimer les caractères spéciaux
    filename = re.sub(r'[^\w\s-]', '', filename)
    filename = re.sub(r'[-\s]+', '_', filename)
    
    # Limiter la longueur
    return filename.strip('_')[:100]

@youtube_bp.route("/info", methods=["GET"])
def get_video_info():
    """Obtient les informations d'une vidéo YouTube"""
    url = request.args.get("url")
    
    if not url:
        return jsonify({"error": "Paramètre 'url' manquant"}), 400

    try:
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": False,
            "writesubtitles": False,
            "writeautomaticsub": False,
        }

        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info is None:
                return jsonify({"error": "Impossible d'obtenir les informations de la vidéo"}), 400

            # Formater les informations utiles
            video_info = {
                "title": info.get("title", "Titre non disponible"),
                "duration": info.get("duration", 0),
                "thumbnail": info.get("thumbnail"),
                "channel": info.get("uploader", "Chaîne inconnue"),
                "views": info.get("view_count", 0),
                "description": (info.get("description", "")[:200] + "...") if info.get("description") else "",
                "id": info.get("id"),
                "formats_available": len(info.get("formats", []))
            }

            return jsonify(video_info)

    except Exception as e:
        error_msg = str(e)
        current_app.logger.error(f"Erreur lors de l'extraction des infos YouTube: {error_msg}")
        
        if "Video unavailable" in error_msg or "Private video" in error_msg:
            return jsonify({"error": "Cette vidéo n'est pas accessible (privée, supprimée ou géo-restreinte)"}), 400
        elif "Sign in to confirm your age" in error_msg:
            return jsonify({"error": "Cette vidéo nécessite une vérification d'âge"}), 400
        else:
            return jsonify({"error": f"Erreur: {error_msg}"}), 500

@youtube_bp.route('/download', methods=['POST'])
def download_video():
    """Télécharge une vidéo YouTube"""
    # Vérifier FFmpeg d'abord
    ffmpeg_available, ffmpeg_result = verify_ffmpeg()
    if not ffmpeg_available:
        return jsonify({"error": f"FFmpeg requis: {ffmpeg_result}"}), 500

    ffmpeg_path = ffmpeg_result
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({"error": "URL manquante"}), 400

    url = data['url']
    format_type = data.get('format', 'video')
    quality = data.get('quality', 'highest')

    # LOGGING DÉTAILLÉ POUR DEBUG
    current_app.logger.info(f"=== DEBUG QUALITÉ AMÉLIORÉ ===")
    current_app.logger.info(f"URL: {url}")
    current_app.logger.info(f"Format demandé: {format_type}")
    current_app.logger.info(f"Qualité demandée: {quality}")
    
    # Créer un dossier temporaire unique
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Configuration yt-dlp
        if format_type == "audio":
            format_string = "bestaudio/best"
            current_app.logger.info(f"Format audio utilisé: {format_string}")
            ydl_opts = {
                "format": format_string,
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "postprocessors": [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                "ffmpeg_location": ffmpeg_path,
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
            }
        else:
            format_string = get_format_string(quality)
            current_app.logger.info(f"Format vidéo utilisé: {format_string}")
            ydl_opts = {
                "format": format_string,
                "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
                "ffmpeg_location": ffmpeg_path,
                "quiet": False,  # Activé pour voir les détails
                "no_warnings": False,  # Activé pour voir les warnings
                "noplaylist": True,
                "merge_output_format": "mp4",
                # Options pour forcer la meilleure qualité
                "writesubtitles": False,
                "writeautomaticsub": False,
                "ignoreerrors": False,
                # Préférer les formats de haute qualité
                "prefer_ffmpeg": True,
                "keepvideo": False,
            }

        current_app.logger.info(f"Options yt-dlp: {ydl_opts}")

        # Télécharger la vidéo
        with YoutubeDL(ydl_opts) as ydl:
            current_app.logger.info(f"Début téléchargement: {url}")
            
            # D'abord extraire les infos pour voir les formats disponibles
            info = ydl.extract_info(url, download=False)
            if not info:
                return jsonify({"error": "Impossible d'extraire les informations de la vidéo"}), 400

            # LOGGING DÉTAILLÉ DES FORMATS DISPONIBLES
            current_app.logger.info(f"Titre: {info.get('title', 'N/A')}")
            current_app.logger.info(f"Formats disponibles: {len(info.get('formats', []))}")
            
            if 'formats' in info:
                # Trier les formats par qualité pour voir les meilleurs
                formats = info['formats']
                video_formats = [f for f in formats if f.get('vcodec') != 'none' and f.get('height')]
                video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
                
                current_app.logger.info("=== TOP 10 FORMATS VIDÉO DISPONIBLES ===")
                for i, fmt in enumerate(video_formats[:10]):
                    current_app.logger.info(f"{i+1}. ID: {fmt.get('format_id', 'N/A')}, "
                                          f"Résolution: {fmt.get('height', 'N/A')}p, "
                                          f"Codec: {fmt.get('vcodec', 'N/A')}, "
                                          f"Ext: {fmt.get('ext', 'N/A')}, "
                                          f"FPS: {fmt.get('fps', 'N/A')}")
                
                # Afficher le format qui sera sélectionné
                selected_format = ydl._format_selection(info, format_string)
                current_app.logger.info(f"Format sélectionné par yt-dlp: {selected_format}")
            
            # Maintenant télécharger avec le format optimal
            current_app.logger.info(f"Démarrage du téléchargement avec format: {format_string}")
            info = ydl.extract_info(url, download=True)
            
            if not info:
                return jsonify({"error": "Impossible de télécharger la vidéo"}), 400

            # Trouver le fichier téléchargé
            downloaded_files = [f for f in os.listdir(temp_dir) if os.path.isfile(os.path.join(temp_dir, f))]
            
            if not downloaded_files:
                return jsonify({"error": "Aucun fichier généré"}), 500

            downloaded_file = os.path.join(temp_dir, downloaded_files[0])
            
            # LOGGING DU FICHIER TÉLÉCHARGÉ
            file_size = os.path.getsize(downloaded_file)
            current_app.logger.info(f"Fichier téléchargé: {downloaded_file}")
            current_app.logger.info(f"Taille du fichier: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
            current_app.logger.info(f"=== FIN DEBUG QUALITÉ AMÉLIORÉ ===")
            
            # Générer un nom de fichier sûr pour le téléchargement
            safe_title = sanitize_filename(info.get('title', 'video'))
            if format_type == "audio":
                download_name = f"{safe_title}.mp3"
            else:
                download_name = f"{safe_title}.mp4"

            current_app.logger.info(f"Téléchargement réussi: {downloaded_file}")

            @after_this_request
            def cleanup(response):
                try:
                    shutil.rmtree(temp_dir)
                except Exception as e:
                    current_app.logger.error(f"Erreur de nettoyage: {str(e)}")
                return response

            return send_file(
                downloaded_file,
                as_attachment=True,
                download_name=download_name,
                mimetype='audio/mpeg' if format_type == "audio" else 'video/mp4'
            )

    except Exception as e:
        # Nettoyage en cas d'erreur
        try:
            shutil.rmtree(temp_dir)
        except:
            pass
        
        error_msg = str(e)
        current_app.logger.error(f"Erreur de téléchargement: {error_msg}")
        
        if "requested format not available" in error_msg.lower():
            return jsonify({"error": "Format demandé non disponible pour cette vidéo"}), 400
        elif "video unavailable" in error_msg.lower():
            return jsonify({"error": "Vidéo non disponible"}), 400
        else:
            return jsonify({"error": f"Erreur de téléchargement: {error_msg}"}), 500

@youtube_bp.route("/test", methods=["GET"])
def test_dependencies():
    """Endpoint de test pour vérifier les dépendances"""
    result = {
        "yt_dlp": False,
        "ffmpeg": False,
        "errors": []
    }
    
    # Test yt-dlp
    try:
        import yt_dlp
        result["yt_dlp"] = True
        result["yt_dlp_version"] = yt_dlp.version.__version__
    except ImportError as e:
        result["errors"].append(f"yt-dlp non installé: {str(e)}")
    
    # Test FFmpeg
    ffmpeg_available, ffmpeg_result = verify_ffmpeg()
    result["ffmpeg"] = ffmpeg_available
    if ffmpeg_available:
        result["ffmpeg_path"] = ffmpeg_result
    else:
        result["errors"].append(ffmpeg_result)
    
    return jsonify(result)