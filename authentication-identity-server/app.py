from flask import Flask, request, jsonify
import jwt
import requests
import json
from jwt import algorithms

app = Flask(__name__)

# URL lấy public keys từ Keycloak
KEYCLOAK_CERTS_URL = "http://localhost:8081/realms/flask-app/protocol/openid-connect/certs"
AUDIENCE = "account"  # hoặc audience của bạn

def get_public_keys():
    try:
        resp = requests.get(KEYCLOAK_CERTS_URL)
        resp.raise_for_status()
        return resp.json()["keys"]
    except Exception as e:
        print("Error fetching keys:", e)
        return []

def token_required(f):
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization", None)
        if not auth or not auth.startswith("Bearer "):
            return jsonify({"error": "Missing token"}), 401

        token = auth.split(" ")[1]
        keys = get_public_keys()
        if not keys:
            return jsonify({"error": "No public keys found"}), 500

        try:
            # Lấy kid từ header token
            token_header = jwt.get_unverified_header(token)
            kid = token_header.get("kid")
            key_data = next((k for k in keys if k["kid"] == kid), None)
            if not key_data:
                return jsonify({"error": "Public key not found for token"}), 401

            # Chuyển JWK sang PEM
            public_key = algorithms.RSAAlgorithm.from_jwk(json.dumps(key_data))

            # Decode token
            jwt.decode(token, public_key, algorithms=["RS256"], audience=AUDIENCE)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({"error": "Invalid token", "detail": str(e)}), 401
        except Exception as e:
            return jsonify({"error": "Token verification failed", "detail": str(e)}), 401

        return f(*args, **kwargs)
    return decorated

@app.route("/secure")
@token_required
def secure():
    return jsonify({"message": "Access granted to /secure"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)