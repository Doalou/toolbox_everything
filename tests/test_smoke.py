"""Tests smoke : routes principales, health, PDF fallback."""

from __future__ import annotations


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "yt_dlp" in data


def test_index_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Toolbox" in resp.data


def test_youtube_index(client):
    resp = client.get("/youtube/")
    assert resp.status_code == 200


def test_media_index(client):
    resp = client.get("/media/")
    assert resp.status_code == 200


def test_essentials_index(client):
    resp = client.get("/essentials/")
    assert resp.status_code == 200


def test_pdf_fallback_when_not_configured(client, app):
    """Sans STIRLING_PDF_URL, la page explique comment configurer."""
    prev = app.config.get("STIRLING_PDF_URL")
    app.config["STIRLING_PDF_URL"] = ""
    try:
        resp = client.get("/pdf/")
        assert resp.status_code == 200
        assert b"Stirling" in resp.data
    finally:
        app.config["STIRLING_PDF_URL"] = prev or ""


def test_pdf_status_not_configured(client, app):
    prev = app.config.get("STIRLING_PDF_URL")
    app.config["STIRLING_PDF_URL"] = ""
    try:
        resp = client.get("/pdf/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["enabled"] is False
    finally:
        app.config["STIRLING_PDF_URL"] = prev or ""


def test_404_returns_html(client):
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404


def test_essentials_redirect(client):
    resp = client.get("/essentials", follow_redirects=False)
    assert resp.status_code in (301, 302, 308)


def test_youtube_info_requires_url(client):
    resp = client.get("/youtube/info")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_youtube_download_requires_body(client):
    resp = client.post("/youtube/download", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
