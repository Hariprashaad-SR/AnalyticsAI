from argon2 import PasswordHasher, exceptions

_pwd = PasswordHasher()

def hash_password(password: str) -> str:
    """Generate Argon2 hash for a plain password."""
    return _pwd.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify plain password against Argon2 hash."""
    try:
        return _pwd.verify(hashed_password, plain_password)
    except exceptions.VerifyMismatchError:
        return False
    except Exception as e:
        print("Error verifying password:", e)
        return False