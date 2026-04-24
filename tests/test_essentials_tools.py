"""Tests unitaires des outils essentiels (sans Flask)."""

from __future__ import annotations

import pytest

from app.services.essentials.tools import (Base64Encoder, ColorPaletteGenerator,
                                            HashCalculator, JSONFormatter,
                                            PasswordGenerator, QRCodeGenerator,
                                            TextProcessor, TimestampConverter)


def test_password_length_and_types():
    pw = PasswordGenerator().generate(length=20)
    assert len(pw) == 20
    # au moins 3 des 4 types de caractères (par construction)
    has_lower = any(c.islower() for c in pw)
    has_upper = any(c.isupper() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    assert sum([has_lower, has_upper, has_digit]) >= 2


def test_password_invalid_when_nothing_selected():
    with pytest.raises(ValueError):
        PasswordGenerator().generate(
            length=12,
            uppercase=False,
            lowercase=False,
            numbers=False,
            symbols=False,
        )


def test_base64_roundtrip():
    encoder = Base64Encoder()
    plain = "Toolbox Everything 🚀"
    encoded = encoder.encode(plain)
    assert encoder.decode(encoded) == plain


def test_hash_sha256_stable():
    h = HashCalculator().calculate("hello", "sha256")
    assert h["algorithm"] == "sha256"
    assert h["hash"] == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"


def test_hash_rejects_unknown_algorithm():
    with pytest.raises(ValueError):
        HashCalculator().calculate("x", "does-not-exist")


def test_qr_code_returns_data_uri():
    data = QRCodeGenerator().generate("hello world")
    assert data.startswith("data:image/png;base64,")
    assert len(data) > 200


def test_text_analyze_basic():
    result = TextProcessor().analyze("Hello world.\nAnother line.")
    stats = result["statistics"]
    assert stats["words"] == 4
    assert stats["lines"] == 2
    assert stats["sentences"] == 2


def test_text_format_operations():
    tp = TextProcessor()
    assert tp.format_text("hello", "uppercase") == "HELLO"
    assert tp.format_text("HELLO", "lowercase") == "hello"
    assert tp.format_text("hello world", "reverse") == "dlrow olleh"


def test_color_palette_generates_count():
    palette = ColorPaletteGenerator().generate("#3B82F6", "complementary", 4)
    assert len(palette) == 4
    for item in palette:
        assert item["hex"].startswith("#")
        assert item["rgb"].startswith("rgb(")


def test_json_formatter_format_and_minify():
    formatter = JSONFormatter()
    result = formatter.process('{"a": 1, "b": [1, 2]}', "format")
    assert result["is_valid"] is True
    assert "formatted" in result
    assert "\n" in result["formatted"]

    minified = formatter.process('{"a": 1}', "minify")
    assert minified["minified"] == '{"a":1}'


def test_json_formatter_invalid():
    result = JSONFormatter().process("{not valid", "format")
    assert result["is_valid"] is False
    assert "error" in result


def test_timestamp_roundtrip():
    tc = TimestampConverter()
    d = tc.timestamp_to_date(0)
    assert d["iso"].startswith("1970-01-01")

    back = tc.date_to_timestamp("1970-01-01 00:00:00")
    assert back["timestamp"] == 0
