from modules.auth.domain.services.password_hasher import IPasswordHasher
from core.security import verify_password, get_password_hash


class BcryptPasswordHasher(IPasswordHasher):
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        return verify_password(plain_password, hashed_password)

    def hash(self, plain_password: str) -> str:
        return get_password_hash(plain_password)
