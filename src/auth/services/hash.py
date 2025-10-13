from hashlib import sha256


def hash_user_password(password: str) -> str:
    return sha256(password.encode()).hexdigest()
