"""
產品數據種子腳本

從前端 mockProducts 數據生成並插入到資料庫的 products 表
執行方式：
  cd backend
  python -m scripts.seed_products
"""
import asyncio
import sys
import os

# 將 backend/src 添加到 Python 路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from infrastructure.database import Base
from modules.product.infrastructure.models import ProductModel, ProductImageModel
import uuid

# 資料庫連接 URL（從環境變數獲取，或使用預設值）
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@localhost:5432/ecommerce"
)

# 前端 mockProducts 數據
MOCK_PRODUCTS = [
    {
        "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "name": "智慧型手機 X",
        "description": "最新的智慧型手機，擁有強大的處理器與相機。",
        "price": 29900,
        "image_url": "https://placehold.co/300x200?text=Phone",
        "stock_quantity": 100,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
        "name": "藍牙耳機 Pro",
        "description": "主動降噪，高音質無線耳機。",
        "price": 5990,
        "image_url": "https://placehold.co/300x200?text=Headphone",
        "stock_quantity": 200,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f",
        "name": "純棉T恤",
        "description": "舒適透氣，百分之百純棉。",
        "price": 490,
        "image_url": "https://placehold.co/300x200?text=T-Shirt",
        "stock_quantity": 500,
        "category": "服飾",
        "is_active": True
    },
    {
        "id": "d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a",
        "name": "多功能背包",
        "description": "防水耐磨，適合旅行與日常使用。",
        "price": 1290,
        "image_url": "https://placehold.co/300x200?text=Bag",
        "stock_quantity": 300,
        "category": "配件",
        "is_active": True
    },
    {
        "id": "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b",
        "name": "機械鍵盤",
        "description": "青軸手感，RGB背光。",
        "price": 2490,
        "image_url": "https://placehold.co/300x200?text=Keyboard",
        "stock_quantity": 150,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c",
        "name": "高級咖啡機",
        "description": "一鍵式操作，享受專業級咖啡。",
        "price": 8990,
        "image_url": "https://placehold.co/300x200?text=CoffeeMachine",
        "stock_quantity": 80,
        "category": "家電",
        "is_active": True
    },
    {
        "id": "a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d",
        "name": "智能手環",
        "description": "追蹤您的健康與運動數據。",
        "price": 1590,
        "image_url": "https://placehold.co/300x200?text=SmartBand",
        "stock_quantity": 250,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "b8c9d0e1-f2a3-4b4c-5d6e-7f8a9b0c1d2e",
        "name": "無線充電板",
        "description": "兼容多款手機，快速無線充電。",
        "price": 790,
        "image_url": "https://placehold.co/300x200?text=WirelessCharger",
        "stock_quantity": 300,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "c9d0e1f2-a3b4-4c5d-6e7f-8a9b0c1d2e3f",
        "name": "舒適懶人沙發",
        "description": "符合人體工學，享受放鬆時光。",
        "price": 3500,
        "image_url": "https://placehold.co/300x200?text=Sofa",
        "stock_quantity": 50,
        "category": "家具",
        "is_active": True
    },
    {
        "id": "d0e1f2a3-b4c5-4d6e-7f8a-9b0c1d2e3f4a",
        "name": "專業運動鞋",
        "description": "輕量透氣，提供卓越的支撐。",
        "price": 2800,
        "image_url": "https://placehold.co/300x200?text=Sneakers",
        "stock_quantity": 200,
        "category": "鞋類",
        "is_active": True
    },
    {
        "id": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b",
        "name": "多功能電烤箱",
        "description": "烘焙、燒烤一機搞定。",
        "price": 4500,
        "image_url": "https://placehold.co/300x200?text=Oven",
        "stock_quantity": 60,
        "category": "家電",
        "is_active": True
    },
    {
        "id": "f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c",
        "name": "高質感錢包",
        "description": "真皮材質，多卡位設計。",
        "price": 1800,
        "image_url": "https://placehold.co/300x200?text=Wallet",
        "stock_quantity": 150,
        "category": "配件",
        "is_active": True
    },
    {
        "id": "a3b4c5d6-e7f8-4a9b-0c1d-2e3f4a5b6c7d",
        "name": "超輕薄筆記型電腦",
        "description": "強大效能，隨身攜帶。",
        "price": 35900,
        "image_url": "https://placehold.co/300x200?text=Laptop",
        "stock_quantity": 40,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "b4c5d6e7-f8a9-4b0c-1d2e-3f4a5b6c7d8e",
        "name": "電競滑鼠",
        "description": "高DPI，精準定位。",
        "price": 1290,
        "image_url": "https://placehold.co/300x200?text=Mouse",
        "stock_quantity": 300,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f",
        "name": "抗藍光眼鏡",
        "description": "保護眼睛，減緩疲勞。",
        "price": 990,
        "image_url": "https://placehold.co/300x200?text=Glasses",
        "stock_quantity": 200,
        "category": "配件",
        "is_active": True
    },
    {
        "id": "d6e7f8a9-b0c1-4d2e-3f4a-5b6c7d8e9f0a",
        "name": "空氣清淨機",
        "description": "有效過濾PM2.5，還你清新空氣。",
        "price": 4990,
        "image_url": "https://placehold.co/300x200?text=AirPurifier",
        "stock_quantity": 80,
        "category": "家電",
        "is_active": True
    },
    {
        "id": "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b",
        "name": "吸塵器",
        "description": "強大吸力，清潔無死角。",
        "price": 6990,
        "image_url": "https://placehold.co/300x200?text=Vacuum",
        "stock_quantity": 70,
        "category": "家電",
        "is_active": True
    },
    {
        "id": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
        "name": "瑜珈墊",
        "description": "加厚防滑，適合各種瑜珈動作。",
        "price": 690,
        "image_url": "https://placehold.co/300x200?text=YogaMat",
        "stock_quantity": 400,
        "category": "運動健身",
        "is_active": True
    },
    {
        "id": "a9b0c1d2-e3f4-4a5b-6c7d-8e9f0a1b2c3d",
        "name": "運動水壺",
        "description": "大容量，耐摔材質。",
        "price": 390,
        "image_url": "https://placehold.co/300x200?text=WaterBottle",
        "stock_quantity": 500,
        "category": "運動健身",
        "is_active": True
    },
    {
        "id": "b0c1d2e3-f4a5-4b6c-7d8e-9f0a1b2c3d4e",
        "name": "簡約風格檯燈",
        "description": "護眼燈光，可調節亮度。",
        "price": 890,
        "image_url": "https://placehold.co/300x200?text=Lamp",
        "stock_quantity": 150,
        "category": "居家",
        "is_active": True
    },
    {
        "id": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
        "name": "人體工學椅",
        "description": "久坐不累，保護脊椎。",
        "price": 5990,
        "image_url": "https://placehold.co/300x200?text=Chair",
        "stock_quantity": 60,
        "category": "家具",
        "is_active": True
    },
    {
        "id": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
        "name": "真皮皮帶",
        "description": "經典款式，百搭耐用。",
        "price": 790,
        "image_url": "https://placehold.co/300x200?text=Belt",
        "stock_quantity": 200,
        "category": "配件",
        "is_active": True
    },
    {
        "id": "e3f4a5b6-c7d8-4e9f-0a1b-2c3d4e5f6a7b",
        "name": "休閒長褲",
        "description": "舒適修身，適合各種場合。",
        "price": 890,
        "image_url": "https://placehold.co/300x200?text=Pants",
        "stock_quantity": 300,
        "category": "服飾",
        "is_active": True
    },
    {
        "id": "f4a5b6c7-d8e9-4f0a-1b2c-3d4e5f6a7b8c",
        "name": "連帽外套",
        "description": "保暖時尚，秋冬必備。",
        "price": 1590,
        "image_url": "https://placehold.co/300x200?text=Hoodie",
        "stock_quantity": 250,
        "category": "服飾",
        "is_active": True
    },
    {
        "id": "a5b6c7d8-e9f0-4a1b-2c3d-4e5f6a7b8c9d",
        "name": "藍牙音響",
        "description": "360度環繞音效，防水設計。",
        "price": 2290,
        "image_url": "https://placehold.co/300x200?text=Speaker",
        "stock_quantity": 120,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "b6c7d8e9-f0a1-4b2c-3d4e-5f6a7b8c9d0e",
        "name": "拍立得相機",
        "description": "即拍即得，紀錄美好時刻。",
        "price": 2990,
        "image_url": "https://placehold.co/300x200?text=Camera",
        "stock_quantity": 90,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "c7d8e9f0-a1b2-4c3d-4e5f-6a7b8c9d0e1f",
        "name": "微波爐",
        "description": "快速加熱，方便實用。",
        "price": 2500,
        "image_url": "https://placehold.co/300x200?text=Microwave",
        "stock_quantity": 100,
        "category": "家電",
        "is_active": True
    },
    {
        "id": "d8e9f0a1-b2c3-4d4e-5f6a-7b8c9d0e1f2a",
        "name": "果汁機",
        "description": "新鮮果汁，健康生活。",
        "price": 1200,
        "image_url": "https://placehold.co/300x200?text=Juicer",
        "stock_quantity": 150,
        "category": "家電",
        "is_active": True
    },
    {
        "id": "e9f0a1b2-c3d4-4e5f-6a7b-8c9d0e1f2a3b",
        "name": "登山鞋",
        "description": "防水透氣，抓地力強。",
        "price": 3500,
        "image_url": "https://placehold.co/300x200?text=HikingShoes",
        "stock_quantity": 100,
        "category": "鞋類",
        "is_active": True
    },
    {
        "id": "f0a1b2c3-d4e5-4f6a-7b8c-9d0e1f2a3b4c",
        "name": "露營帳篷",
        "description": "輕量化設計，快速搭建。",
        "price": 4500,
        "image_url": "https://placehold.co/300x200?text=Tent",
        "stock_quantity": 50,
        "category": "戶外用品",
        "is_active": True
    },
    {
        "id": "01b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "name": "行動電源",
        "description": "大容量，支援快充。",
        "price": 990,
        "image_url": "https://placehold.co/300x200?text=PowerBank",
        "stock_quantity": 400,
        "category": "電子產品",
        "is_active": True
    },
    {
        "id": "12c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
        "name": "平板電腦",
        "description": "輕薄便攜，影音娛樂首選。",
        "price": 12900,
        "image_url": "https://placehold.co/300x200?text=Tablet",
        "stock_quantity": 80,
        "category": "電子產品",
        "is_active": True
    }
]


async def seed_products():
    """插入產品種子數據"""
    # 從環境變數讀取資料庫連接
    from infrastructure.config import settings

    engine = create_async_engine(settings.database_url, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # 檢查是否已有產品
        result = await session.execute(select(ProductModel).limit(1))
        if result.scalar_one_or_none():
            print("⚠️ 資料庫已有產品數據，跳過種子插入")
            await engine.dispose()
            return

        print("📦 開始插入產品數據...")

        for product_data in MOCK_PRODUCTS:
            product_id = uuid.UUID(product_data['id'])
            product = ProductModel(
                id=product_id,
                name=product_data['name'],
                description=product_data['description'],
                price=product_data['price'],
                stock_quantity=product_data.get('stock_quantity', 100),
                category=product_data.get('category'),
                is_active=product_data.get('is_active', True)
            )
            session.add(product)
            
            # 加入圖片
            product_image = ProductImageModel(
                product_id=product_id,
                url=product_data['image_url'],
                alt_text=product_data['name'],
                is_primary=True
            )
            session.add(product_image)
            
            print(f"  ✓ 加入: {product.name} (ID: {product.id})")

        await session.commit()
        print(f"✅ 成功插入 {len(MOCK_PRODUCTS)} 個產品")

    await engine.dispose()



if __name__ == "__main__":
    asyncio.run(seed_products())

