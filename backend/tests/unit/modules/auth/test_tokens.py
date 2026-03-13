import pytest
from infrastructure.redis.token_manager import RedisTokenManager
from unittest.mock import AsyncMock, MagicMock

@pytest.mark.asyncio
async def test_store_and_get_verification_token():
    # Arrange
    redis_client = MagicMock()
    redis_client.setex = AsyncMock()
    redis_client.get = AsyncMock(return_value=b"user-123")
    redis_client.delete = AsyncMock()
    
    manager = RedisTokenManager(redis_client)
    token = "test-token"
    user_id = "user-123"

    # Act
    await manager.store_verification_token(user_id, token)
    retrieved_user_id = await manager.get_user_id_by_verify_token(token)

    # Assert
    redis_client.setex.assert_called_once_with(f"auth:verify:{token}", 86400, user_id)
    redis_client.get.assert_called_once_with(f"auth:verify:{token}")
    redis_client.delete.assert_called_once_with(f"auth:verify:{token}")
    assert retrieved_user_id == user_id

@pytest.mark.asyncio
async def test_get_invalid_verification_token():
    # Arrange
    redis_client = MagicMock()
    redis_client.get = AsyncMock(return_value=None)
    
    manager = RedisTokenManager(redis_client)
    
    # Act
    retrieved_user_id = await manager.get_user_id_by_verify_token("invalid")

    # Assert
    assert retrieved_user_id is None

@pytest.mark.asyncio
async def test_store_and_get_reset_token():
    # Arrange
    redis_client = MagicMock()
    redis_client.setex = AsyncMock()
    redis_client.get = AsyncMock(return_value=b"user-456")
    redis_client.delete = AsyncMock()
    
    manager = RedisTokenManager(redis_client)
    token = "reset-token"
    user_id = "user-456"

    # Act
    await manager.store_reset_token(user_id, token)
    retrieved_user_id = await manager.get_user_id_by_reset_token(token)

    # Assert
    redis_client.setex.assert_called_once_with(f"auth:reset:{token}", 3600, user_id)
    redis_client.get.assert_called_once_with(f"auth:reset:{token}")
    redis_client.delete.assert_called_once_with(f"auth:reset:{token}")
    assert retrieved_user_id == user_id
