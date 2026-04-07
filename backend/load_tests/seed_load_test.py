"""
壓力測試資料種子腳本

在 Docker 容器內執行，直接寫入 PostgreSQL 和 Redis。
建立測試商品、用戶、JWT token、Redis 購物車。

執行方式：
  docker exec ecommerce_api python -m load_tests.seed_load_test --num-users 100 --stock 10
  docker exec ecommerce_api python -m load_tests.seed_load_test --reset-only --stock 10
"""

import asyncio
import argparse
import json
import sys
import os
import uuid
from datetime import datetime, timezone

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text
import redis.asyncio as aioredis

from infrastructure.config import settings
from modules.auth.infrastructure.models import UserModel
from modules.product.infrastructure.models import ProductModel
from core.security import get_password_hash, create_access_token

# 固定測試商品 UUID
PRODUCT_ID = uuid.UUID("00000000-0000-4000-8000-100d7e570001")
PRODUCT_NAME = "Load Test Product"
PRODUCT_PRICE = 99.99

OUTPUT_FILE = "/app/load_tests/users.json"


def parse_args():
    parser = argparse.ArgumentParser(description="Seed load test data")
    parser.add_argument(
        "--num-users", type=int, default=100, help="Number of test users (default: 100)"
    )
    parser.add_argument(
        "--stock", type=int, default=10, help="Product stock quantity (default: 10)"
    )
    parser.add_argument(
        "--reset-only",
        action="store_true",
        help="Only reset stock and carts (skip user creation)",
    )
    return parser.parse_args()


async def seed(args):
    engine = create_async_engine(settings.database_url)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    redis_client = await aioredis.from_url(
        settings.redis_url, encoding="utf-8", decode_responses=True
    )

    num_users = args.num_users
    stock = args.stock
    reset_only = args.reset_only

    # --- 密碼只 hash 一次，所有用戶共用 ---
    password_hash = get_password_hash("LoadTest123!")
    print("Password hashed once for all users")

    async with async_session() as session:
        # === 1. 建立/更新測試商品 ===
        result = await session.execute(
            select(ProductModel).where(ProductModel.id == PRODUCT_ID)
        )
        product = result.scalar_one_or_none()

        if product:
            product.stock_quantity = stock
            product.is_active = True
            product.name = PRODUCT_NAME
            product.price = PRODUCT_PRICE
            print(f"Updated product stock to {stock}")
        else:
            product = ProductModel(
                id=PRODUCT_ID,
                name=PRODUCT_NAME,
                description="Product for load testing",
                price=PRODUCT_PRICE,
                stock_quantity=stock,
                is_active=True,
            )
            session.add(product)
            print(f"Created test product with stock={stock}")

        await session.flush()

        # === 2. 建立用戶（如非 reset-only）===
        if not reset_only:
            # 查詢已存在的 loadtest 用戶
            result = await session.execute(
                select(UserModel).where(UserModel.email.like("loadtest_%@test.com"))
            )
            existing_users = {u.email: u for u in result.scalars().all()}
            print(f"Found {len(existing_users)} existing loadtest users")

            new_count = 0
            for i in range(num_users):
                email = f"loadtest_{i:04d}@test.com"
                if email not in existing_users:
                    user = UserModel(
                        id=uuid.uuid4(),
                        email=email,
                        username=f"loadtest_{i:04d}",
                        password_hash=password_hash,
                        role="user",
                        is_verified=True,
                        is_active=True,
                    )
                    session.add(user)
                    new_count += 1

            if new_count > 0:
                await session.flush()
            print(f"Created {new_count} new users (total needed: {num_users})")

        await session.commit()

        # === 3. 重新查詢所有 loadtest 用戶（取得 ID）===
        result = await session.execute(
            select(UserModel)
            .where(UserModel.email.like("loadtest_%@test.com"))
            .order_by(UserModel.email)
            .limit(num_users)
        )
        users = result.scalars().all()
        print(f"Loaded {len(users)} users for token generation")

    # === 4. 生成 JWT token ===
    users_data = []
    for user in users:
        token = create_access_token(
            {
                "sub": user.email,
                "user_id": str(user.id),
                "role": "user",
            }
        )
        users_data.append(
            {
                "user_id": str(user.id),
                "email": user.email,
                "token": token,
            }
        )

    print(f"Generated {len(users_data)} JWT tokens")

    # === 5. Redis 購物車批量寫入 ===
    now = datetime.now(timezone.utc).isoformat()
    product_id_str = str(PRODUCT_ID)
    cart_data = json.dumps(
        {
            "product_id": product_id_str,
            "quantity": 1,
            "created_at": now,
            "updated_at": now,
        }
    )

    # 先清除舊的購物車
    pipe = redis_client.pipeline(transaction=False)
    for ud in users_data:
        pipe.delete(f"cart:{ud['user_id']}")
    await pipe.execute()

    # 批量寫入新購物車
    pipe = redis_client.pipeline(transaction=False)
    for ud in users_data:
        cart_key = f"cart:{ud['user_id']}"
        pipe.hset(cart_key, product_id_str, cart_data)
        pipe.expire(cart_key, 86400)  # 24h TTL
    await pipe.execute()

    print(f"Set up {len(users_data)} Redis carts")

    # === 5.5. 初始化 Redis 庫存 key（stock:{product_id}）===
    await redis_client.set(f"stock:{product_id_str}", stock)
    print(f"Initialized Redis stock key: stock:{product_id_str} = {stock}")

    # === 6. 清除該商品的舊訂單（避免干擾測試結果）===
    async with async_session() as session:
        await session.execute(
            text("""
                DELETE FROM order_items WHERE product_id = :pid
            """),
            {"pid": str(PRODUCT_ID)},
        )
        await session.execute(text("""
                DELETE FROM orders WHERE id NOT IN (
                    SELECT DISTINCT order_id FROM order_items
                ) AND user_id IN (
                    SELECT id FROM users WHERE email LIKE 'loadtest_%@test.com'
                )
            """))
        await session.commit()
        print("Cleaned up old loadtest orders")

    # === 7. 輸出 users.json ===
    with open(OUTPUT_FILE, "w") as f:
        json.dump(users_data, f)
    print(f"Wrote {len(users_data)} users to {OUTPUT_FILE}")

    await redis_client.close()
    await engine.dispose()
    print("Done!")


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(seed(args))
