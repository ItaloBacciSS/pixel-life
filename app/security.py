import os
from urllib.parse import urlsplit

from flask import abort, request

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'; "
       "object-src 'none'; base-uri 'none'; form-action 'self'; frame-ancestors 'none'")
HEADERS = {
    "Content-Security-Policy": CSP,
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "same-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}


def init_security(app):
    @app.before_request
    def same_origin_only():
        """Recusa pedidos que alteram dados vindos de outro site (defesa extra além do cookie SameSite)."""
        if request.method in SAFE_METHODS:
            return
        if request.headers.get("Sec-Fetch-Site") == "cross-site":
            abort(403)
        origin = request.headers.get("Origin")
        if origin and urlsplit(origin).netloc != request.host:
            abort(403)

    @app.after_request
    def security_headers(response):
        for name, value in HEADERS.items():
            response.headers.setdefault(name, value)
        if os.environ.get("VERCEL"):
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        return response
