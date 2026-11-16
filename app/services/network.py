import hashlib
import os

from flask import request


def client_ip():
    """IP de quem fez o pedido. Na Vercel o IP real vem nos cabeçalhos que ela mesma define."""
    if os.environ.get("VERCEL"):
        forwarded = request.headers.get("X-Real-IP") or request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
    return request.remote_addr or "desconhecido"


def fingerprint(prefix):
    """Chave curta derivada do IP (o IP em si não é guardado no banco)."""
    return f"{prefix}:{hashlib.sha256(client_ip().encode()).hexdigest()[:16]}"
