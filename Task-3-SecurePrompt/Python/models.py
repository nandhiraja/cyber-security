from datetime import datetime, timezone
from extensions import db
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

ph = PasswordHasher(
    time_cost=3,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(512), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    def set_password(self, plaintext: str) -> None:
        self.password_hash = ph.hash(plaintext)

    def verify_password(self, plaintext: str) -> bool:
        try:
            return ph.verify(self.password_hash, plaintext)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    def __repr__(self) -> str:
        return f"<User id={self.id}>"
