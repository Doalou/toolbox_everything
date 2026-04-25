"""Tests smoke : routes principales, health, PDF fallback."""

from __future__ import annotations

from pathlib import Path


def test_health_ok(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "ok"
    assert "version" in data
    assert "yt_dlp" in data
    assert data["tailwind_css"] is True


def test_index_renders(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Toolbox" in resp.data
    assert b"v1.3.1" in resp.data
    assert b"Speedtest" in resp.data
    assert b"/speedtest/" in resp.data


def test_version_file_is_release_source():
    assert Path("VERSION").read_text(encoding="utf-8").strip() == "1.3.1"


def test_base_template_loads_local_css_assets(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"css/tailwind.css" in resp.data
    assert b"css/style.css" in resp.data


def test_header_controls_are_csp_safe(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b'id="themeToggle"' in resp.data
    assert b'header-icon-button--mobile' in resp.data
    assert b"onclick=" not in resp.data


def test_main_pages_do_not_use_inline_click_handlers(client):
    for path in ("/", "/media/", "/essentials/", "/pdf/", "/speedtest/"):
        resp = client.get(path)
        assert resp.status_code == 200
        assert b"onclick=" not in resp.data, f"{path} contient encore un onclick inline"


def test_main_pages_have_clean_visible_copy(client):
    forbidden = [
        "—",
        "–",
        "…",
        "quelques clics",
        "tout-en-un",
        "utile et propre",
        "embarque",
    ]
    for path in ("/", "/downloader/", "/media/", "/essentials/", "/pdf/", "/speedtest/"):
        resp = client.get(path)
        assert resp.status_code == 200
        html = resp.data.decode("utf-8", errors="replace")
        found = [token for token in forbidden if token in html]
        assert not found, f"{path} contient encore {found}"


def test_responsive_header_css_is_not_overridden():
    from pathlib import Path

    css = Path("app/static/css/style.css").read_text(encoding="utf-8")
    assert ".site-header__nav-center {\n    display: none;" in css
    assert "@media (min-width: 1180px)" in css
    assert ".header-icon-button--mobile" in css
    assert ".media-file-grid" in css
    assert ".home-card-grid" in css


def test_downloader_index(client):
    resp = client.get("/downloader/")
    assert resp.status_code == 200


def test_legacy_youtube_redirects_to_downloader(client):
    """Compat ascendante après le rename /youtube → /downloader (v1.3.1)."""
    resp = client.get("/youtube/", follow_redirects=False)
    assert resp.status_code in (301, 308)
    assert "/downloader" in resp.headers["Location"]


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


def test_speedtest_fallback_when_not_configured(client, app):
    """Sans LIBRESPEED_URL, la page explique comment configurer."""
    prev = app.config.get("LIBRESPEED_URL")
    app.config["LIBRESPEED_URL"] = ""
    try:
        resp = client.get("/speedtest/")
        assert resp.status_code == 200
        assert b"LibreSpeed" in resp.data
    finally:
        app.config["LIBRESPEED_URL"] = prev or ""


def test_speedtest_status_not_configured(client, app):
    prev = app.config.get("LIBRESPEED_URL")
    app.config["LIBRESPEED_URL"] = ""
    try:
        resp = client.get("/speedtest/status")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["enabled"] is False
    finally:
        app.config["LIBRESPEED_URL"] = prev or ""


def test_speedtest_redirect(client):
    resp = client.get("/speedtest", follow_redirects=False)
    assert resp.status_code in (301, 302, 308)


def test_404_returns_html(client):
    resp = client.get("/this-route-does-not-exist")
    assert resp.status_code == 404


def test_essentials_redirect(client):
    resp = client.get("/essentials", follow_redirects=False)
    assert resp.status_code in (301, 302, 308)


def test_downloader_info_requires_url(client):
    resp = client.get("/downloader/info")
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data


def test_downloader_download_requires_body(client):
    resp = client.post("/downloader/download", json={})
    assert resp.status_code == 400
    data = resp.get_json()
    assert "error" in data
