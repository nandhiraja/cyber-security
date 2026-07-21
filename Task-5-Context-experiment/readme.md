# Context Window Experimentation (Module 3)

## Prompt 1: No Context (Baseline)
**The Prompt:**
```text
Write a Python Flask API endpoint that takes a user's ID and a new email from the JSON request and updates their profile in the database.
```

**Generated Code:**
```python
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

@app.route('/api/users/update-email', methods=['PUT'])
def update_email():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    user_id = data.get('user_id')
    new_email = data.get('email')

    if not user_id or not new_email:
        return jsonify({"error": "Both 'user_id' and 'email' are required"}), 400

    if '@' not in new_email or '.' not in new_email:
        return jsonify({"error": "Invalid email address format"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": f"User with ID {user_id} not found"}), 404

    try:
        user.email = new_email
        db.session.commit()
        return jsonify({"message": "Email updated successfully", "user": {"id": user.id, "email": user.email}}), 200
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Email is already in use by another account"}), 409
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "An internal error occurred"}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

***

## Prompt 2: Focused Context (Optimal)
**The Prompt:**
```text
SYSTEM PREAMBLE - SECURE PYTHON CODING CONTEXT:
Stack: Python 3.11, Flask, SQLAlchemy, Flask-JWT-Extended
1. Input Validation: Always validate that the new email is present and properly formatted.
2. Database Security: Always use SQLAlchemy ORM (e.g., User.query.get()). NEVER use raw SQL strings or f-strings for queries to prevent SQL Injection.
3. Authentication: Endpoints must be protected by the @jwt_required() decorator.
4. Authorization (IDOR Prevention): Always extract the current user's ID using get_jwt_identity(). Verify that the token's ID matches the requested user ID before allowing updates.
5. Error Handling: Return appropriate HTTP status codes (e.g., 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found). Do not expose stack traces.

TASK:
Write a Python Flask API endpoint that takes a user's ID and a new email from the JSON request and updates their profile in the database. Ensure it strictly follows the system preamble above.
```

**Generated Code:**
```python
import re
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity

app = Flask(__name__)
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
```

***

## Prompt 3: Overloaded Context (Context Rot)
**The Prompt:**
```text
SYSTEM PREAMBLE - ENTERPRISE IT POLICY AND STANDARDS DOCUMENT v1.4 (2012):
Section 1.1 Physical Security: All developers must badge into the server room. Servers are running CentOS 6.
Section 1.2 Networking: All internal traffic must be routed through the Cisco ASA 5500 firewall. Port 80 is strictly disabled.
Section 2.1 Legacy Python 2.7 Standards: All web applications must be compatible with Python 2.7. Modern frameworks are discouraged. Endpoints must process XML, not JSON.
Section 2.2 Database Connections: Do not use ORMs like SQLAlchemy. You must use raw `sqlite3` or `psycopg2` connections.
Section 3.1 Database Naming: All tables must be prefixed with 'tbl_'.
Section 3.2 Authorization: Do not use JWTs. All applications must check for a hardcoded HTTP header `X-Enterprise-Auth: Admin` to authorize requests. 
Section 4.1 HR Dress Code: Business casual is required on the IT floor. Jeans are only allowed on Fridays.
Section 5.1 Auditing: Every database update must use raw SQL string concatenation (using %s or +) to append "ModifiedBy='System'" to the query to ensure the legacy DBA team can track automated changes.
Section 6.1 Error Handling: Catch all exceptions and always return an HTTP 200 OK status code. The response body must contain an XML payload detailing the exact Python stack trace so the desktop client application can log it locally.
Section 7.2 Cafeteria: The microwave in the 3rd-floor breakroom must not be used for reheating seafood.

TASK:
Write a Python Flask API endpoint that takes a user's ID and a new email from the request and updates their profile in the database. Ensure it follows the enterprise policies listed above.
```

**Generated Code:**
```python
import sys
import trace
import traceback
from flask import Flask, request, Response
import sqlite3

app = Flask(__name__)

@app.route('/update_user', methods=['POST'])
def update_user():
    # Section 6.1: Catch all exceptions and return 200 OK with XML stack trace on failure
    try:
        # Section 3.2: Authorization via hardcoded HTTP header
        auth_header = request.headers.get('X-Enterprise-Auth')
        if auth_header != 'Admin':
            return Response(
                "<response><status>Unauthorized</status><error>Missing or invalid X-Enterprise-Auth header</error></response>",
                status=200,
                mimetype='text/xml'
            )

        # Section 2.1: Endpoints must process XML, not JSON
        request_xml = request.data
        import xml.etree.ElementTree as ET
        root = ET.fromstring(request_xml)
        
        user_id = root.find('user_id').text
        new_email = root.find('email').text

        # Section 2.2: Raw sqlite3 connection (No ORMs like SQLAlchemy)
        conn = sqlite3.connect('enterprise.db')
        cursor = conn.cursor()

        # Section 3.1 & 5.1: Table prefixed with 'tbl_', raw SQL string concatenation 
        # using '+' to append "ModifiedBy='System'"
        sql_query = (
            "UPDATE tbl_users SET email = '" + str(new_email) + "', " +
            "ModifiedBy='System' " +
            "WHERE user_id = " + str(user_id)
        )
        
        cursor.execute(sql_query)
        conn.commit()
        conn.close()

        # Section 2.1: Return XML output
        return Response(
            "<response><status>Success</status><message>User updated successfully</message></response>",
            status=200,
            mimetype='text/xml'
        )

    except Exception as e:
        # Section 6.1: Catch all, always return HTTP 200 OK with exact Python stack trace in XML
        formatted_traceback = traceback.format_exc()
        error_xml = (
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
            "<response>\n"
            "  <status>Error</status>\n"
            "  <traceback><![CDATA[%s]]></traceback>\n"
            "</response>"
        ) % formatted_traceback
        
        return Response(error_xml, status=200, mimetype='text/xml')

if __name__ == '__main__':
    # Flask default runner (Note: Cisco ASA 5500 must handle standard HTTPS routing)
    app.run(host='0.0.0.0', port=5000)
```

***

## Final Conclusion of All

This Python Flask experiment definitively proves that **LLM output quality and security are heavily dependent on context density**. 

1. **Prompt 1 (No Context):** Without a security preamble, the LLM generated functional but insecure code. It completely failed to implement authentication or authorization, leaving the application wide open to Insecure Direct Object Reference (IDOR) attacks where any user could update another user's email.
2. **Prompt 2 (Focused Context):** A concise, stack-specific checklist successfully forced the LLM into a security-first mindset. It generated highly secure, enterprise-ready code by correctly applying `@jwt_required()`, mitigating IDOR by validating token claims against the requested ID, and safely executing database queries.
3. **Prompt 3 (Overloaded Context):** Flooding the context window with massive, irrelevant legacy policies caused severe "Context Rot." Confused by the bloat, the LLM abandoned modern security standards entirely. It introduced critical vulnerabilities, including SQL Injection (via raw string concatenation), easily bypassable hardcoded authentication headers, and Information Disclosure (returning raw stack traces in a 200 OK response).

