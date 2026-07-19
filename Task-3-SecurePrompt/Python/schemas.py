import re
from marshmallow import Schema, fields, validate, ValidationError, pre_load

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")

MAX_EMAIL_LENGTH = 254
MIN_PASSWORD_LENGTH = 8
MAX_PASSWORD_LENGTH = 128


class LoginSchema(Schema):
    email = fields.String(
        required=True,
        load_default=None,
        validate=[
            validate.Length(min=3, max=MAX_EMAIL_LENGTH,
                            error=f"Email must be between 3 and {MAX_EMAIL_LENGTH} characters."),
        ],
    )
    password = fields.String(
        required=True,
        load_default=None,
        validate=[
            validate.Length(min=MIN_PASSWORD_LENGTH, max=MAX_PASSWORD_LENGTH,
                            error=f"Password must be between {MIN_PASSWORD_LENGTH} and {MAX_PASSWORD_LENGTH} characters."),
        ],
    )

    @pre_load
    def strip_and_normalise(self, data: dict, **kwargs) -> dict:
        if isinstance(data.get("email"), str):
            data["email"] = data["email"].strip().lower()
        return data

    def validate_email_format(self, email: str) -> bool:
        return bool(EMAIL_REGEX.match(email))


login_schema = LoginSchema()
