"""
REST API для взаимодействия с Minecraft плагином.
Minecraft плагин обращается сюда для генерации кодов и проверки привязки.
"""

from flask import Flask, request, jsonify
from functools import wraps
import database as db
from config import API_SECRET

app = Flask(__name__)


def require_secret(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get("X-API-Secret", "")
        if token != API_SECRET:
            return jsonify({"error": "Unauthorized"}), 401
        return f(*args, **kwargs)
    return decorated


@app.route("/api/generate_code", methods=["POST"])
@require_secret
def generate_code():
    """
    Вызывается плагином когда игрок пишет /link.
    Body: {"uuid": "...", "nick": "..."}
    """
    data = request.json or {}
    uuid = data.get("uuid", "").strip()
    nick = data.get("nick", "").strip()
    if not uuid or not nick:
        return jsonify({"error": "uuid and nick required"}), 400

    code = db.generate_code(uuid, nick)
    return jsonify({"code": code, "expires_minutes": 10})


@app.route("/api/check_link", methods=["GET"])
@require_secret
def check_link():
    """
    Проверяет, привязан ли игрок.
    Query: ?uuid=...
    """
    uuid = request.args.get("uuid", "").strip()
    if not uuid:
        return jsonify({"error": "uuid required"}), 400

    row = db.get_link_by_uuid(uuid)
    if row:
        return jsonify({
            "linked": True,
            "platform": row["platform"],
            "user_id": row["user_id"],
            "linked_at": row["linked_at"],
        })
    return jsonify({"linked": False})


@app.route("/api/get_link_by_nick", methods=["GET"])
@require_secret
def get_link_by_nick():
    nick = request.args.get("nick", "").strip()
    if not nick:
        return jsonify({"error": "nick required"}), 400

    row = db.get_link_by_nick(nick)
    if row:
        return jsonify({
            "linked": True,
            "platform": row["platform"],
            "user_id": row["user_id"],
            "minecraft_uuid": row["minecraft_uuid"],
        })
    return jsonify({"linked": False})


def run_api():
    from config import API_HOST, API_PORT
    app.run(host=API_HOST, port=API_PORT)
