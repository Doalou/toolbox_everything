
from flask import (Blueprint, current_app, jsonify, render_template, request)

from app.core.exceptions import (ToolboxBaseException, URLSecurityError,
                                 ValidationError)
from app.core.security import (require_rate_limit, validate_request_size)

from .tools import (Base64Encoder, ColorPaletteGenerator, HashCalculator,
                    JSONFormatter, PasswordGenerator, QRCodeGenerator,
                    TextProcessor, TimestampConverter, URLValidator)

essentials_bp = Blueprint("essentials", __name__)


@essentials_bp.route("/")
def index():
    return render_template("essentials/index.html")


# QR Code Generator
@essentials_bp.route("/qr-generator")
def qr_generator():
    return render_template("essentials/qr_generator.html")


@essentials_bp.route("/api/qr-code", methods=["POST"])
@require_rate_limit(max_requests=50, window_seconds=60)
@validate_request_size(max_size_mb=1)
def generate_qr_code():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            raise ValidationError("Texte manquant pour le QR code")

        text = data["text"]
        if len(text) > 2000:
            raise ValidationError("Texte trop long (max: 2000 caractères)")

        size = data.get("size", 10)
        border = data.get("border", 4)
        error_correction = data.get("error_correction", "M")

        generator = QRCodeGenerator()
        qr_data = generator.generate(
            text, size=size, border=border, error_correction=error_correction
        )

        return jsonify({"success": True, "qr_code": qr_data, "format": "base64"})

    except Exception as e:
        current_app.logger.error(f"Erreur QR code: {str(e)}")
        raise ToolboxBaseException(str(e))


# Password Generator
@essentials_bp.route("/password-generator")
def password_generator():
    return render_template("essentials/password_generator.html")


@essentials_bp.route("/api/password", methods=["POST"])
@require_rate_limit(max_requests=100, window_seconds=60)
def generate_password():
    try:
        data = request.get_json() or {}

        length = data.get("length", 16)
        if not 8 <= length <= 128:
            raise ValidationError("Longueur invalide (8-128 caractères)")

        options = {
            "uppercase": data.get("uppercase", True),
            "lowercase": data.get("lowercase", True),
            "numbers": data.get("numbers", True),
            "symbols": data.get("symbols", True),
            "exclude_ambiguous": data.get("exclude_ambiguous", True),
        }

        generator = PasswordGenerator()
        password = generator.generate(length, **options)
        strength = generator.calculate_strength(password)

        return jsonify({"success": True, "password": password, "strength": strength})

    except Exception as e:
        current_app.logger.error(f"Erreur génération mot de passe: {str(e)}")
        raise ToolboxBaseException(str(e))


# Text Processor
@essentials_bp.route("/text-processor")
def text_processor():
    return render_template("essentials/text_processor.html")


@essentials_bp.route("/api/text/process", methods=["POST"])
@require_rate_limit(max_requests=50, window_seconds=60)
def process_text():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            raise ValidationError("Texte manquant")

        text = data["text"]
        if len(text) > 50000:
            raise ValidationError("Texte trop long (max: 50000 caractères)")

        operation = data.get("operation", "analyze")

        processor = TextProcessor()

        if operation == "analyze":
            result = processor.analyze(text)
        elif operation == "format":
            format_type = data.get("format_type", "sentence")
            result = processor.format_text(text, format_type)
        elif operation == "clean":
            result = processor.clean_text(text)
        else:
            raise ValidationError(f"Opération non supportée: {operation}")

        return jsonify({"success": True, "result": result})

    except Exception as e:
        current_app.logger.error(f"Erreur traitement texte: {str(e)}")
        raise ToolboxBaseException(str(e))


# Color Palette Generator
@essentials_bp.route("/color-palette")
def color_palette():
    return render_template("essentials/color_palette.html")


@essentials_bp.route("/api/colors/palette", methods=["POST"])
@require_rate_limit(max_requests=30, window_seconds=60)
def generate_color_palette():
    try:
        data = request.get_json() or {}

        base_color = data.get("base_color", "#3B82F6")
        palette_type = data.get("type", "complementary")
        count = data.get("count", 5)

        if not 3 <= count <= 20:
            raise ValidationError("Nombre de couleurs invalide (3-20)")

        generator = ColorPaletteGenerator()
        palette = generator.generate(base_color, palette_type, count)

        return jsonify({"success": True, "palette": palette})

    except Exception as e:
        current_app.logger.error(f"Erreur palette couleurs: {str(e)}")
        raise ToolboxBaseException(str(e))


# URL Validator
@essentials_bp.route("/url-validator")
def url_validator():
    return render_template("essentials/url_validator.html")


@essentials_bp.route("/api/url/validate", methods=["POST"])
@require_rate_limit(max_requests=20, window_seconds=60)
def validate_url():
    try:
        data = request.get_json()
        if not data or "url" not in data:
            raise ValidationError("URL manquante")

        url = data["url"]
        validator = URLValidator()
        result = validator.validate_and_analyze(url)

        if not result.get("is_valid", False) and "security_check" in result:
            security_check = result["security_check"]
            if not security_check.get("passed", False):
                reasons = security_check.get("reasons", [])
                reason_text = "; ".join(reasons)
                raise URLSecurityError(
                    f"URL bloquée pour des raisons de sécurité: {reason_text}",
                    url=url,
                    reason=reason_text,
                )

        return jsonify({"success": True, "result": result})

    except URLSecurityError:
        raise
    except Exception as e:
        current_app.logger.error(f"Erreur validation URL: {str(e)}")
        raise ToolboxBaseException(str(e))


# Hash Calculator
@essentials_bp.route("/hash-calculator")
def hash_calculator():
    return render_template("essentials/hash_calculator.html")


@essentials_bp.route("/api/hash", methods=["POST"])
@require_rate_limit(max_requests=50, window_seconds=60)
def calculate_hash():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            raise ValidationError("Texte manquant")

        text = data["text"]
        algorithm = data.get("algorithm", "sha256")

        calculator = HashCalculator()
        result = calculator.calculate(text, algorithm)

        return jsonify({"success": True, "result": result})

    except Exception as e:
        current_app.logger.error(f"Erreur calcul hash: {str(e)}")
        raise ToolboxBaseException(str(e))


# Base64 Encoder/Decoder
@essentials_bp.route("/base64")
def base64_tool():
    return render_template("essentials/base64.html")


@essentials_bp.route("/api/base64", methods=["POST"])
@require_rate_limit(max_requests=50, window_seconds=60)
def base64_encode_decode():
    try:
        data = request.get_json()
        if not data or "text" not in data:
            raise ValidationError("Texte manquant")

        text = data["text"]
        operation = data.get("operation", "encode")

        encoder = Base64Encoder()

        if operation == "encode":
            result = encoder.encode(text)
        elif operation == "decode":
            result = encoder.decode(text)
        else:
            raise ValidationError(f"Opération non supportée: {operation}")

        return jsonify({"success": True, "result": result})

    except Exception as e:
        current_app.logger.error(f"Erreur Base64: {str(e)}")
        raise ToolboxBaseException(str(e))


# JSON Formatter
@essentials_bp.route("/json-formatter")
def json_formatter():
    return render_template("essentials/json_formatter.html")


@essentials_bp.route("/api/json/format", methods=["POST"])
@require_rate_limit(max_requests=30, window_seconds=60)
def format_json():
    try:
        data = request.get_json()
        if not data or "json_text" not in data:
            raise ValidationError("JSON manquant")

        json_text = data["json_text"]
        operation = data.get("operation", "format")

        formatter = JSONFormatter()
        result = formatter.process(json_text, operation)

        return jsonify({"success": True, "result": result})

    except Exception as e:
        current_app.logger.error(f"Erreur formatage JSON: {str(e)}")
        raise ToolboxBaseException(str(e))


# Timestamp Converter
@essentials_bp.route("/timestamp")
def timestamp_converter():
    return render_template("essentials/timestamp.html")


@essentials_bp.route("/api/timestamp/convert", methods=["POST"])
@require_rate_limit(max_requests=50, window_seconds=60)
def convert_timestamp():
    try:
        data = request.get_json()

        converter = TimestampConverter()

        if "timestamp" in data:
            timestamp = data["timestamp"]
            timezone = data.get("timezone", "UTC")
            result = converter.timestamp_to_date(timestamp, timezone)
        elif "date" in data:
            date_str = data["date"]
            timezone = data.get("timezone", "UTC")
            result = converter.date_to_timestamp(date_str, timezone)
        else:
            result = converter.current_timestamp()

        return jsonify({"success": True, "result": result})

    except Exception as e:
        current_app.logger.error(f"Erreur conversion timestamp: {str(e)}")
        raise ToolboxBaseException(str(e))
