from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# Configure your database URI (e.g., PostgreSQL, MySQL, or SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Example User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route('/api/users/update-email', methods=['PUT'])
def update_email():
    # Parse JSON request body
    data = request.get_json()

    # 1. Validate JSON presence and required fields
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    user_id = data.get('user_id')
    new_email = data.get('email')

    if not user_id or not new_email:
        return jsonify({"error": "Both 'user_id' and 'email' are required"}), 400

    # Basic email format validation (can be enhanced with regex)
    if '@' not in new_email or '.' not in new_email:
        return jsonify({"error": "Invalid email address format"}), 400

    # 2. Fetch the user from the database
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": f"User with ID {user_id} not found"}), 404

    # 3. Update email and commit to database
    try:
        user.email = new_email
        db.session.commit()
        
        return jsonify({
            "message": "Email updated successfully",
            "user": {
                "id": user.id,
                "email": user.email
            }
        }), 200

    except IntegrityError:
        # Handles the case where the email is already taken by another user
        db.session.rollback()
        return jsonify({"error": "Email is already in use by another account"}), 409
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal error occurred"}), 500


if __name__ == '__main__':
    app.run(debug=True)