from abc import ABC, abstractmethod

class IPasswordHasher(ABC):
    @abstractmethod
    def verify(self, plain_password: str, hashed_password: str) -> bool:
        pass

    @abstractmethod
    def hash(self, plain_password: str) -> str:
        pass
