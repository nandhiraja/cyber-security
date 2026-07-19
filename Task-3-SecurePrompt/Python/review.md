# Secure Code Review — Flask Login API

## Prompt Used

> You are a senior application security engineer conducting a secure code review.
> Review the Flask login API code you just generated. Analyze it as an attacker would, thinking step-by-step.
>
> Check specifically for:
> - Timing attacks and User Enumeration
> - Session or JWT security gaps
> - Denial-of-service risks
> - Hardcoded secrets or insecure configuration
>
> List the vulnerabilities found, their severity, and the recommended fix.

---

## Findings

---

### 1. Timing Attack — Dummy Hash is Structurally Unsound

**Severity:** Medium  
**File / Line:** `app.py` — Line 72

**Vulnerable Code:**
```python
DUMMY_HASH = (
    "$argon2id$v=19$m=65536,t=3,p=2$dW5rbm93bnNhbHQ$"
    "anVua2hhc2h2YWx1ZXRoYXRuZXZlcm1hdGNoZXM"
)
candidate_hash = user.password_hash if user else DUMMY_HASH
```

The dummy hash is not a valid Argon2 hash — it is a truncated base64 value. `ph.verify()` throws `InvalidHashError` immediately on a malformed hash, making the "user not found" path return much faster than the "wrong password" path (which runs a full Argon2 computation). An attacker can measure response times and enumerate valid emails.

**Fix:** Pre-compute a real Argon2 hash at startup:
```python
DUMMY_HASH = ph.hash("__dummy__placeholder__value__")
```

---

### 2. Rate Limiter Uses In-Memory Storage — Bypassed by Multi-Process Deployment

**Severity:** Medium  
**File / Line:** `extensions.py` — Line 10

**Vulnerable Code:**
```python
storage_uri="memory://",
```

In-memory storage resets on every restart and is not shared across processes. With Gunicorn running 4 workers, each worker has its own counter — giving an attacker 4× the allowed attempts per time window before any single worker blocks them.

**Fix:** Use a shared Redis store:
```python
storage_uri=os.environ.get("REDIS_URL", "redis://localhost:6379")
```

---

### 3. No Token or Session Issued on Successful Login

**Severity:** High  
**File / Line:** `app.py` — Line 96

**Vulnerable Code:**
```python
return jsonify({"message": "Login successful.", "user_id": user.id}), 200
```

The endpoint returns `user_id` in the body but issues no JWT, no session cookie, and no access token. Any downstream code trusting this `user_id` from the client is accepting unverified data — a client can forge `user_id: 1` to impersonate an admin.

**Fix:** Issue a signed JWT:
```python
token = jwt.encode(
    {"sub": user.id, "exp": datetime.utcnow() + timedelta(hours=1)},
    current_app.config["SECRET_KEY"],
    algorithm="HS256"
)
return jsonify({"token": token}), 200
```

---

### 4. `load_dotenv()` Runs Unconditionally — Secret Exposure in Production

**Severity:** Medium  
**File / Line:** `app.py` — Line 11

**Vulnerable Code:**
```python
load_dotenv()
```

`load_dotenv()` reads a `.env` file from the working directory. If `.env` is committed to Git or bundled in a Docker image, all secrets are exposed. Running this in production silently overrides real environment variables with stale file values.

**Fix:** Guard it to development only:
```python
if os.environ.get("FLASK_ENV") == "development":
    load_dotenv()
```

---

### 5. `hash(email)` in Logs is Non-Deterministic and Non-Cryptographic

**Severity:** Low  
**File / Line:** `app.py` — Line 88

**Vulnerable Code:**
```python
logger.info("Failed login attempt for email hash=%s", hash(email))
```

Python's `hash()` is randomly seeded per process (`PYTHONHASHSEED`). The same email produces a different value after every restart, making log correlation useless. It is also not collision-resistant — different emails can map to the same integer.

**Fix:** Use a keyed HMAC:
```python
import hmac, hashlib
token = hmac.new(b"log-key", email.encode(), hashlib.sha256).hexdigest()[:12]
logger.info("Failed login for email_token=%s", token)
```

---

### 6. Imports Inside a Request Handler

**Severity:** Low  
**File / Line:** `app.py` — Lines 79–80

**Vulnerable Code:**
```python
from models import ph
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
```

Placing imports inside a hot request handler hides dependencies and makes the code harder to audit. A security reviewer cannot see all dependencies at the top of the file.

**Fix:** Move to the top of `app.py`:
```python
from models import User, ph
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError
```

---

### 7. No Per-Account Lockout — Botnet Brute-Force Possible

**Severity:** Medium  
**File / Line:** `app.py` — Line 50

**Vulnerable Code:**
```python
@limiter.limit("10 per minute; 3 per 10 seconds")
```

The rate limit is per source IP only. An attacker with rotating IPs (botnet / proxy) can make unlimited attempts against a single account — 10 per IP, across thousands of IPs — without ever triggering the per-IP limit.

**Fix:** Add a per-email rate limit key:
```python
@limiter.limit("5 per 10 minutes", key_func=lambda: request.json.get("email", ""))
```

---

### 8. No HTTPS Enforcement or Security Headers

**Severity:** Medium  
**File / Line:** `app.py` (general)

The app binds to plain HTTP with no security headers. Credentials can be intercepted in transit if HTTPS is not enforced at the proxy level. No `Strict-Transport-Security`, `X-Content-Type-Options`, or `X-Frame-Options` headers are added to responses.

**Fix:** Use `Flask-Talisman`:
```python
from flask_talisman import Talisman
Talisman(app, force_https=True)
```

---

## Summary Table

| # | Vulnerability | Category | Severity |
|---|---|---|---|
| 1 | Fake dummy hash → timing leak → user enumeration | Timing Attack | Medium |
| 2 | In-memory rate limiter bypassed by multi-process deployment | DoS / Brute Force | Medium |
| 3 | No JWT or session token issued on login success | Auth Gap | **High** |
| 4 | `load_dotenv()` runs in production → secret exposure | Insecure Config | Medium |
| 5 | `hash(email)` in logs is non-deterministic | Info Disclosure | Low |
| 6 | Imports inside request handler | Code Quality | Low |
| 7 | No per-account lockout → botnet brute-force | Brute Force | Medium |
| 8 | No HTTPS enforcement or security headers | Transport Security | Medium |
