import io
import os
import subprocess
import uuid
import zipfile

from flask import (Blueprint, current_app, jsonify, render_template, request,
                   send_file)
from PIL import Image
from werkzeug.utils import secure_filename

media_bp = Blueprint("media", __name__)


@media_bp.route("/")
def index():
    return render_template("media.html")


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_MEDIA_EXTENSIONS"]
    )


def is_video(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in current_app.config["ALLOWED_VIDEO_EXTENSIONS"]
    )


def process_image(img, output_format, quality=85):
    """Traite une image"""
    output = io.BytesIO()

    try:
        if output_format == "JPEG":
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(output, format=output_format, quality=quality, optimize=True)
        else:
            img.save(output, format=output_format, optimize=True)

        output.seek(0)
        return output
    except Exception as e:
        raise ValueError(f"Erreur lors du traitement de l'image: {str(e)}")


def process_video(input_path, output_path, quality=85):
    """Conversion vidéo avec FFmpeg"""
    try:
        ffmpeg_path = current_app.config.get("FFMPEG_PATH")
        if not ffmpeg_path or not os.path.exists(ffmpeg_path):
            ffmpeg_path = "/usr/bin/ffmpeg"
            if not os.path.exists(ffmpeg_path):
                raise ValueError("FFmpeg n'est pas disponible")

        command = [
            ffmpeg_path,
            "-i",
            input_path,
            "-y",
        ]

        output_format = os.path.splitext(output_path)[1][1:]
        if output_format == "mp4":
            command.extend(
                [
                    "-c:v",
                    "libx264",
                    "-preset",
                    "medium",
                    "-crf",
                    "23",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "128k",
                ]
            )
        elif output_format == "webm":
            command.extend(
                [
                    "-c:v",
                    "libvpx-vp9",
                    "-crf",
                    "30",
                    "-b:v",
                    "0",
                    "-c:a",
                    "libopus",
                    "-deadline",
                    "good",
                    "-cpu-used",
                    "1",
                ]
            )

        command.append(output_path)

        current_app.logger.info(f"Commande FFmpeg: {' '.join(command)}")
        current_app.logger.info("Début conversion - timeout: 600 secondes")

        _ = subprocess.run(
            command, capture_output=True, text=True, check=True, timeout=600
        )

        if not os.path.exists(output_path):
            raise ValueError("La conversion n'a pas généré de fichier de sortie")

        output_size = os.path.getsize(output_path)
        current_app.logger.info(
            f"Conversion terminée avec succès - taille: {output_size} bytes"
        )

        return output_path

    except subprocess.TimeoutExpired:
        current_app.logger.error("Timeout de conversion FFmpeg (10 minutes)")
        raise ValueError("La conversion a pris trop de temps (limite: 10 minutes)")
    except subprocess.CalledProcessError as e:
        current_app.logger.error(f"Erreur FFmpeg: {e.stderr}")
        raise ValueError(f"Erreur lors de la conversion: {e.stderr}")
    except Exception as e:
        current_app.logger.error(f"Erreur: {str(e)}")
        raise


class ResourceManager:
    def __init__(self):
        self.resources = []

    def add(self, resource):
        self.resources.append(resource)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        for resource in self.resources:
            try:
                if os.path.exists(resource):
                    os.remove(resource)
            except Exception as e:
                current_app.logger.error(
                    f"Erreur lors du nettoyage de {resource}: {str(e)}"
                )


@media_bp.route("/convert", methods=["POST"])
def convert_media():
    if "file" not in request.files:
        return jsonify({"error": "Fichier manquant"}), 400

    file = request.files["file"]
    if not file or not file.filename:
        return jsonify({"error": "Fichier invalide"}), 400

    try:
        temp_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], "temp")
        os.makedirs(temp_dir, exist_ok=True)

        input_filename = secure_filename(file.filename)
        output_format = request.form.get("format", "").lower()
        quality = int(request.form.get("quality", 85))

        input_path = os.path.join(temp_dir, f"input_{uuid.uuid4()}_{input_filename}")
        output_path = os.path.join(temp_dir, f"output_{uuid.uuid4()}.{output_format}")

        file.save(input_path)
        current_app.logger.info(f"Fichier reçu: {input_path}")

        try:
            if is_video(file.filename):
                current_app.logger.info(
                    f"Début conversion vidéo: {input_path} -> {output_path}"
                )
                result_path = process_video(input_path, output_path, quality)
                response = send_file(
                    result_path,
                    as_attachment=True,
                    download_name=f"converted_{os.path.splitext(input_filename)[0]}.{output_format}",
                )
            else:
                img = Image.open(input_path)
                output = process_image(img, output_format.upper(), quality)
                response = send_file(
                    output,
                    mimetype=f"image/{output_format.lower()}",
                    as_attachment=True,
                    download_name=f"converted_{os.path.splitext(input_filename)[0]}.{output_format}",
                )

            return response

        finally:
            for path in [input_path, output_path]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception as e:
                        current_app.logger.error(
                            f"Erreur de nettoyage {path}: {str(e)}"
                        )

    except Exception as e:
        current_app.logger.error(f"Erreur de conversion: {str(e)}")
        return jsonify({"error": str(e)}), 500


@media_bp.route("/batch", methods=["POST"])
def batch_process():
    """Traite plusieurs images en batch"""
    if "files[]" not in request.files:
        return jsonify({"error": "Aucun fichier transmis"}), 400

    files = request.files.getlist("files[]")

    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, "w") as zf:
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
        mimetype="application/zip",
        as_attachment=True,
        download_name="processed_images.zip",
    )
