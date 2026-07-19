import os
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from marshmallow import ValidationError

from extensions import db, limiter
from models import User
from schemas import login_schema, EMAIL_REGEX

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        raise RuntimeError("DATABASE_URL environment variable is required.")

    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    secret_key = os.environ.get("SECRET_KEY")
    if not secret_key or len(secret_key) < 32:
        raise RuntimeError("SECRET_KEY must be set and at least 32 characters long.")
    app.config["SECRET_KEY"] = secret_key

    db.init_app(app)
    limiter.init_app(app)

    register_routes(app)

    return app


def register_routes(app: Flask) -> None:

    @app.route("/api/login", methods=["POST"])
    @limiter.limit("10 per minute; 3 per 10 seconds")
    def login():
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json."}), 415

        raw = request.get_json(silent=True)
        if raw is None:
            return jsonify({"error": "Request body must be valid JSON."}), 400

        try:
            data = login_schema.load(raw)
        except ValidationError as exc:
            return jsonify({"error": "Invalid input.", "details": exc.messages}), 400

        email: str = data["email"]
        password: str = data["password"]

        if not EMAIL_REGEX.match(email):
            return jsonify({"error": "Invalid input.", "details": {"email": ["Not a valid email address."]}}), 400

        user: User | None = User.query.filter_by(email=email).first()

        DUMMY_HASH = (
            "$argon2id$v=19$m=65536,t=3,p=2$dW5rbm93bnNhbHQ$"
            "anVua2hhc2h2YWx1ZXRoYXRuZXZlcm1hdGNoZXM"
        )
        candidate_hash = user.password_hash if user else DUMMY_HASH
        is_active = user.is_active if user else False

        from models import ph
        from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
        verified = False
        try:
            verified = ph.verify(candidate_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            verified = False

        if not verified or not is_active:
            logger.info("Failed login attempt for email hash=%s", hash(email))
            return jsonify({"error": "Invalid credentials."}), 401

        if ph.check_needs_rehash(user.password_hash):
            user.set_password(password)
            db.session.commit()

        logger.info("Successful login for user_id=%s", user.id)
        return jsonify({"message": "Login successful.", "user_id": user.id}), 200

    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        return jsonify({"error": "Too many login attempts. Please try again later."}), 429

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def internal_error(e):
        logger.exception("Unhandled server error")
        return jsonify({"error": "An unexpected error occurred."}), 500


if __name__ == "__main__":
    flask_app = create_app()
    with flask_app.app_context():
        db.create_all()
    debug_mode = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    flask_app.run(debug=debug_mode, host="127.0.0.1", port=5000)
