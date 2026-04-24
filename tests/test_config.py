"""Tests sur la configuration (Config) : chemins et défauts."""

from __future__ import annotations

from config import Config


def test_base_dir_exists():
    import os

    assert os.path.isdir(Config.BASE_DIR)


def test_allowed_extensions_sets():
    assert "jpg" in Config.ALLOWED_IMAGE_EXTENSIONS
    assert "mp4" in Config.ALLOWED_VIDEO_EXTENSIONS
    assert Config.ALLOWED_MEDIA_EXTENSIONS >= Config.ALLOWED_IMAGE_EXTENSIONS
    assert Config.ALLOWED_MEDIA_EXTENSIONS >= Config.ALLOWED_VIDEO_EXTENSIONS


def test_mime_types_contain_common():
    mimes = Config.get_mime_types()
    assert mimes["png"] == "image/png"
    assert mimes["mp4"] == "video/mp4"
    assert mimes["pdf"] == "application/pdf"


def test_max_content_length_reasonable():
    assert Config.MAX_CONTENT_LENGTH > 1024 * 1024
