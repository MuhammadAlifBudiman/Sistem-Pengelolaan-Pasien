"""
UI regression tests for the Glitch → Northflank migration.

Verifies:
- No active cdn.glitch.global / glitch.me references remain in runtime source files.
- All referenced local image assets exist, are non-empty, and are valid JPEGs/PNGs.
- Exactly one carousel slide carries the 'active' class.
- DataTables CSS and JS versions match in base.html.
- login.js contains an error handler (non-2xx responses produce a toast).
- No secrets introduced in changed files.
- GET /, /login, /register return HTTP 200.
- Static image assets are served by Flask with HTTP 200.
"""
import os
import re
import struct
import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

RUNTIME_DIRS = [
    os.path.join(REPO_ROOT, "static"),
    os.path.join(REPO_ROOT, "templates"),
]

GLITCH_PATTERN = re.compile(
    r"cdn\.glitch\.global|glitch\.me", re.IGNORECASE
)

IMAGES = [
    "static/images/login.jpg",
    "static/images/01.jpg",
    "static/images/05.jpg",
    "static/images/06.jpeg",
    "static/profile_pics/profile_placeholder.png",
]


def _read_file(rel_path):
    with open(os.path.join(REPO_ROOT, rel_path), encoding="utf-8", errors="replace") as fh:
        return fh.read()


def _walk_runtime_source():
    """Yield (relpath, content) for all .html, .css, .js under runtime dirs."""
    for dirpath in RUNTIME_DIRS:
        for root, _dirs, files in os.walk(dirpath):
            for fname in files:
                if fname.endswith((".html", ".css", ".js")):
                    full = os.path.join(root, fname)
                    rel = os.path.relpath(full, REPO_ROOT)
                    with open(full, encoding="utf-8", errors="replace") as fh:
                        yield rel, fh.read()


def _is_jpeg(path):
    with open(path, "rb") as f:
        return f.read(2) == b"\xff\xd8"


def _is_png(path):
    with open(path, "rb") as f:
        return f.read(8) == b"\x89PNG\r\n\x1a\n"


# ---------------------------------------------------------------------------
# 1. No active Glitch CDN references in runtime source files
# ---------------------------------------------------------------------------

def test_no_glitch_references_in_runtime_files():
    violations = []
    for rel, content in _walk_runtime_source():
        if GLITCH_PATTERN.search(content):
            violations.append(rel)
    assert violations == [], (
        "Active cdn.glitch.global / glitch.me refs found in runtime files:\n"
        + "\n".join(f"  {v}" for v in violations)
    )


# ---------------------------------------------------------------------------
# 2. All referenced local images exist, are non-empty, and decodable
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("rel_path", IMAGES)
def test_image_exists_and_valid(rel_path):
    full = os.path.join(REPO_ROOT, rel_path)
    assert os.path.exists(full), f"Missing image: {rel_path}"
    size = os.path.getsize(full)
    assert size > 0, f"Zero-byte image: {rel_path}"
    if rel_path.endswith(".png"):
        assert _is_png(full), f"Not a valid PNG: {rel_path}"
    else:
        assert _is_jpeg(full), f"Not a valid JPEG: {rel_path}"


# ---------------------------------------------------------------------------
# 3. Exactly one carousel slide has the 'active' class
# ---------------------------------------------------------------------------

def test_carousel_exactly_one_active_slide():
    content = _read_file("templates/pages/index.html")
    active_slides = re.findall(r'class="carousel-item\s+active"', content)
    assert len(active_slides) == 1, (
        f"Expected exactly 1 carousel-item active, found {len(active_slides)}"
    )


# ---------------------------------------------------------------------------
# 4. DataTables CSS and JS versions match in base.html
# ---------------------------------------------------------------------------

def test_datatables_versions_match():
    content = _read_file("templates/base/base.html")
    css_m = re.search(r"datatables\.net/([\d.]+)/css/", content, re.IGNORECASE)
    js_m = re.search(r"datatables\.net/([\d.]+)/js/", content, re.IGNORECASE)
    assert css_m, "DataTables CSS URL not found in base.html"
    assert js_m, "DataTables JS URL not found in base.html"
    assert css_m.group(1) == js_m.group(1), (
        f"DataTables version mismatch: CSS={css_m.group(1)} JS={js_m.group(1)}"
    )


# ---------------------------------------------------------------------------
# 5. login.js has an error handler (non-2xx responses produce feedback)
# ---------------------------------------------------------------------------

def test_login_js_has_error_handler():
    content = _read_file("static/js/login.js")
    # Must contain an 'error:' callback in the $.ajax call
    assert re.search(r"\berror\s*:", content), (
        "login.js is missing an error: handler in $.ajax"
    )
    # The handler must call showToast
    assert "showToast" in content, (
        "login.js error handler does not call showToast"
    )


# ---------------------------------------------------------------------------
# 6. No secrets introduced in changed files
# ---------------------------------------------------------------------------

SECRET_PATTERN = re.compile(
    r"mongodb\+srv://[^\"'>\s]+|mongodb://[^\"'>\s]+|"
    r"password\s*=\s*['\"][^'\"]{8,}['\"]|"
    r"SECRET_KEY\s*=\s*['\"][^'\"]{8,}['\"]",
    re.IGNORECASE,
)

CHANGED_FILES = [
    "static/css/login.css",
    "static/css/register.css",
    "templates/pages/index.html",
    "templates/pages/profile.html",
    "templates/base/base.html",
    "static/script.js",
    "static/style.css",
    "static/js/login.js",
    "static/js/index.js",
]


@pytest.mark.parametrize("rel_path", CHANGED_FILES)
def test_no_secrets_in_changed_file(rel_path):
    content = _read_file(rel_path)
    match = SECRET_PATTERN.search(content)
    assert not match, f"Possible secret found in {rel_path}: {match.group()[:40]}"


# ---------------------------------------------------------------------------
# 7. Flask route tests: GET /, /login, /register → 200
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("route", ["/", "/login", "/register"])
def test_public_routes_return_200(app_client, route):
    client, _ = app_client
    resp = client.get(route)
    assert resp.status_code == 200, (
        f"GET {route} returned {resp.status_code}, expected 200"
    )


# ---------------------------------------------------------------------------
# 8. Static image assets served with HTTP 200
# ---------------------------------------------------------------------------

STATIC_IMAGE_ROUTES = [
    "/static/images/login.jpg",
    "/static/images/01.jpg",
    "/static/images/05.jpg",
    "/static/images/06.jpeg",
]


@pytest.mark.parametrize("route", STATIC_IMAGE_ROUTES)
def test_static_images_return_200(app_client, route):
    client, _ = app_client
    resp = client.get(route)
    assert resp.status_code == 200, (
        f"GET {route} returned {resp.status_code}, expected 200"
    )
