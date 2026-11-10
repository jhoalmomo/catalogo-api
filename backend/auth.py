import jwt
from functools import wraps
from flask import request, jsonify
from datetime import datetime, timedelta, timezone

# Clave secreta simétrica fija para firmar y verificar tokens
SECRET_KEY = "clave_secreta_jwt_para_firmar_tokens"

def generar_token(usuario_id, username):
    """Genera un JWT firmado con vigencia de 3 horas."""
    payload = {
        "sub": str(usuario_id),
        "username": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=3)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def token_requerido(f):
    """Decorador middleware para exigir cabecera 'Authorization: Bearer <token>'."""
    @wraps(f)
    def decorador(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({"error": "Cabecera Authorization requerida"}), 401

        partes = auth_header.strip().split(" ")
        if len(partes) != 2 or partes[0] != "Bearer":
            return jsonify({"error": "Formato de token inválido. Use: Bearer <token>"}), 401

        token = partes[1].strip()

        try:
            datos = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            request.usuario_autenticado = datos
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "El token ha expirado. Inicie sesión nuevamente."}), 401
        except jwt.InvalidTokenError as e:
            print(f"[ERROR JWT] Token inválido: {e}")
            return jsonify({"error": "Token no válido o alterado"}), 401

        return f(*args, **kwargs)
    return decorador
