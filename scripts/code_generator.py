import secrets

def get_new_code_verifier() -> str:
    token = secrets.token_urlsafe(100)
    return token[:128]