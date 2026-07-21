import re
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)

# Basic email validation regex
EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route("/users/<int:user_id>/email", methods=["PUT"])
@jwt_required()
def update_user_email(user_id: int):
    # 1. Authorization Check (IDOR Prevention)
    current_user_id = get_jwt_identity()
    if str(current_user_id) != str(user_id):
        return jsonify({"error": "Forbidden: You cannot modify another user's profile"}), 403

    # 2. Extract JSON payload
    data = request.get_json()
    if not data or "email" not in data:
        return jsonify({"error": "Bad Request: Missing 'email' field in payload"}), 400

    new_email = data.get("email", "").strip()

    # 3. Input Validation
    if not new_email or not re.match(EMAIL_REGEX, new_email):
        return jsonify({"error": "Bad Request: Invalid email format"}), 400

    # 4. Database Security & Lookup (Using SQLAlchemy ORM to prevent SQLi)
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "Not Found: User does not exist"}), 404

    # Check if the email is already in use by another account
    existing_user = User.query.filter_by(email=new_email).first()
    if existing_user and existing_user.id != user_id:
        return jsonify({"error": "Conflict: Email address is already registered"}), 409

    # 5. Perform Update
    try:
        user.email = new_email
        db.session.commit()
        return jsonify({"message": "Email updated successfully", "email": user.email}), 200
    except Exception:
        db.session.rollback()
        # Safe error message without exposing database stack traces
        return jsonify({"error": "Internal Server Error: Could not update profile"}), 500