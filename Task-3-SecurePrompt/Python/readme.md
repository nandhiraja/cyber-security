# Task 3 — Secure Login REST API (Python / Flask)

## Prompt Used

> You are a senior security engineer and Python backend developer.
> Using Python 3.11, Flask 3.x, SQLAlchemy, and PostgreSQL, create a secure login REST API endpoint.
>
> Requirements:
> - Follow OWASP Secure Coding Practices.
> - Accept email and password as JSON input. Validate required fields, input types, length, and email format.
> - Use SQLAlchemy ORM. Never construct SQL using string concatenation.
> - Verify passwords using Argon2; never store or compare plaintext passwords.
> - Return generic error messages for invalid login attempts (do not reveal if the email exists).
> - Use appropriate HTTP status codes and add rate-limiting for repeated login attempts.
> - Read credentials from environment variables. Do not hardcode credentials.
> - Do not use eval() or log passwords/PII.

---

## Project Structure

```
Python/
├── app.py            # Flask app + /api/login endpoint
├── models.py         # SQLAlchemy User model with Argon2 helpers
├── schemas.py        # Marshmallow input validation schema
├── extensions.py     # Shared db + limiter instances (avoids circular imports)
├── requirements.txt  # Pinned dependencies
└── .env.example      # Template for environment variables
```

---

## Security Controls Implemented

| OWASP Requirement | How It's Addressed | File / Line |
|---|---|---|
| Input validation — required fields | Marshmallow `required=True` on both fields | `schemas.py` |
| Input validation — types | Marshmallow `fields.String` rejects non-strings | `schemas.py` |
| Input validation — length | `validate.Length(min, max)` on email (3–254) and password (8–128) | `schemas.py` |
| Input validation — email format | Regex `EMAIL_REGEX` checked before DB query | `schemas.py`, `app.py` |
| No string-concatenated SQL | SQLAlchemy ORM `filter_by(email=email)` only | `app.py` |
| Argon2id password hashing | `argon2-cffi` with `time_cost=3, memory_cost=64MB` | `models.py` |
| No plaintext password storage | `set_password()` hashes before storing | `models.py` |
| No plaintext comparison | `verify_password()` uses `ph.verify()`, never `==` | `models.py` |
| Generic error on login failure | Both "email not found" and "wrong password" return `401 Invalid credentials.` | `app.py` |
| Timing-attack prevention | Dummy hash verified even when user doesn't exist | `app.py` |
| Rate limiting | `10 per minute; 3 per 10 seconds` per IP via Flask-Limiter | `app.py` |
| No hardcoded credentials | `DATABASE_URL` and `SECRET_KEY` from `os.environ` | `app.py` |
| No `eval()` | Not used anywhere in the codebase | All files |
| No PII/password logging | Only `user_id` and `hash(email)` logged | `app.py` |
| Argon2 forward security | `check_needs_rehash()` triggers rehash on next login | `app.py` |
| `FLASK_DEBUG=false` in production | `debug_mode` read from env var only | `app.py` |

---

## Setup & Run

```bash
# 1. Create a virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your real PostgreSQL credentials and a strong SECRET_KEY

# 4. Run the app (creates tables on startup)
python app.py
```

---

## API Reference

### `POST /api/login`

**Request**
```json
{
  "email": "user@example.com",
  "password": "your_password"
}
```

**Responses**

| Status | Meaning | Body |
|---|---|---|
| `200` | Login successful | `{ "message": "Login successful.", "user_id": 1 }` |
| `400` | Bad input (missing fields / wrong types / bad email format) | `{ "error": "Invalid input.", "details": {...} }` |
| `401` | Wrong email or password | `{ "error": "Invalid credentials." }` |
| `415` | Wrong Content-Type | `{ "error": "Content-Type must be application/json." }` |
| `429` | Rate limit exceeded | `{ "error": "Too many login attempts. Please try again later." }` |
| `500` | Server error | `{ "error": "An unexpected error occurred." }` |

---