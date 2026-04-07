import asyncio
import uuid
import logging
from sqlalchemy import select
from infrastructure.database import AsyncSessionLocal
from modules.product.infrastructure.models import (
    ProductModel,
    CategoryModel,
    ProductImageModel,
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock Data (Original seed data from frontend/src/services/productService.ts)
MOCK_CATEGORIES = [
    {"id": 1, "name": "3C 數位", "slug": "digital-3c"},
    {"id": 2, "name": "流行服飾", "slug": "fashion"},
    {"id": 3, "name": "生活家電", "slug": "appliances"},
    {"id": 4, "name": "家居生活", "slug": "home-living"},
    {"id": 5, "name": "戶外運動", "slug": "outdoor-sports"},
]

CATEGORY_MAPPING = {
    "c1": 1,
    "c1-1": 1,
    "c1-2": 1,
    "c1-3": 1,
    "c1-4": 1,
    "c2": 2,
    "c2-1": 2,
    "c2-2": 2,
    "c2-3": 2,
    "c3": 3,
    "c3-1": 3,
    "c3-2": 3,
    "c4": 4,
    "c4-1": 4,
    "c4-2": 4,
    "c5": 5,
    "c5-1": 5,
    "c5-2": 5,
}

MOCK_PRODUCTS = [
    {
        "id": "a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "name": "智慧型手機 X",
        "description": "最新的智慧型手機，擁有強大的處理器與相機。",
        "price": 29900,
        "imageUrl": "https://placehold.co/300x200?text=Phone",
        "tags": ["3C 數位", "手機"],
        "is_featured": True,
        "categoryId": "c1-1",
    },
    {
        "id": "b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
        "name": "藍牙耳機 Pro",
        "description": "主動降噪，高音質無線耳機。",
        "price": 5990,
        "imageUrl": "https://placehold.co/300x200?text=Headphone",
        "tags": ["3C 數位", "耳機"],
        "is_featured": True,
        "categoryId": "c1-2",
    },
    {
        "id": "c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f",
        "name": "純棉T恤",
        "description": "舒適透氣，百分之百純棉。",
        "price": 490,
        "imageUrl": "https://placehold.co/300x200?text=T-Shirt",
        "tags": ["流行服飾", "男裝"],
        "categoryId": "c2-1",
    },
    {
        "id": "d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a",
        "name": "多功能背包",
        "description": "防水耐磨，適合旅行與日常使用。",
        "price": 1290,
        "imageUrl": "https://placehold.co/300x200?text=Bag",
        "tags": ["流行服飾", "配件"],
        "is_featured": True,
        "categoryId": "c2-2",
    },
    {
        "id": "e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b",
        "name": "機械鍵盤",
        "description": "青軸手感，RGB背光。",
        "price": 2490,
        "imageUrl": "https://placehold.co/300x200?text=Keyboard",
        "tags": ["3C 數位", "電腦周邊"],
        "categoryId": "c1-3",
    },
    {
        "id": "f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c",
        "name": "高級咖啡機",
        "description": "一鍵式操作，享受專業級咖啡。",
        "price": 8990,
        "imageUrl": "https://placehold.co/300x200?text=CoffeeMachine",
        "tags": ["生活家電", "廚房家電"],
        "is_featured": True,
        "categoryId": "c3-1",
    },
    {
        "id": "a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d",
        "name": "智能手環",
        "description": "追蹤您的健康與運動數據。",
        "price": 1590,
        "imageUrl": "https://placehold.co/300x200?text=SmartBand",
        "tags": ["3C 數位", "穿戴裝置"],
        "is_featured": True,
        "categoryId": "c1-4",
    },
    {
        "id": "b8c9d0e1-f2a3-4b4c-5d6e-7f8a9b0c1d2e",
        "name": "無線充電板",
        "description": "兼容多款手機，快速無線充電。",
        "price": 790,
        "imageUrl": "https://placehold.co/300x200?text=WirelessCharger",
        "tags": ["3C 數位", "手機配件"],
        "is_featured": True,
        "categoryId": "c1",
    },
    {
        "id": "c9d0e1f2-a3b4-4c5d-6e7f-8a9b0c1d2e3f",
        "name": "舒適懶人沙發",
        "description": "符合人體工學，享受放鬆時光。",
        "price": 3500,
        "imageUrl": "https://placehold.co/300x200?text=Sofa",
        "tags": ["家居生活", "生活家電"],
        "categoryId": "c4",
    },
    {
        "id": "d0e1f2a3-b4c5-4d6e-7f8a-9b0c1d2e3f4a",
        "name": "專業運動鞋",
        "description": "輕量透氣，提供卓越的支撐。",
        "price": 2800,
        "imageUrl": "https://placehold.co/300x200?text=Sneakers",
        "tags": ["流行服飾", "運動服飾"],
        "categoryId": "c2-3",
    },
    {
        "id": "e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b",
        "name": "多功能電烤箱",
        "description": "烘焙、燒烤一機搞定。",
        "price": 4500,
        "imageUrl": "https://placehold.co/300x200?text=Oven",
        "tags": ["生活家電", "廚房家電"],
        "is_featured": True,
        "categoryId": "c3-1",
    },
    {
        "id": "f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c",
        "name": "高質感錢包",
        "description": "真皮材質，多卡位設計。",
        "price": 1800,
        "imageUrl": "https://placehold.co/300x200?text=Wallet",
        "tags": ["流行服飾", "配件"],
        "is_featured": True,
        "categoryId": "c2-2",
    },
    {
        "id": "a3b4c5d6-e7f8-4a9b-0c1d-2e3f4a5b6c7d",
        "name": "超輕薄筆記型電腦",
        "description": "強大效能，隨身攜帶。",
        "price": 35900,
        "imageUrl": "https://placehold.co/300x200?text=Laptop",
        "tags": ["3C 數位", "電腦"],
        "categoryId": "c1-3",
    },
    {
        "id": "b4c5d6e7-f8a9-4b0c-1d2e-3f4a5b6c7d8e",
        "name": "電競滑鼠",
        "description": "高DPI，精準定位。",
        "price": 1290,
        "imageUrl": "https://placehold.co/300x200?text=Mouse",
        "tags": ["3C 數位", "電腦周邊"],
        "categoryId": "c1-3",
    },
    {
        "id": "c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f",
        "name": "抗藍光眼鏡",
        "description": "保護眼睛，減緩疲勞。",
        "price": 990,
        "imageUrl": "https://placehold.co/300x200?text=Glasses",
        "tags": ["流行服飾", "配件"],
        "categoryId": "c2-2",
    },
    {
        "id": "d6e7f8a9-b0c1-4d2e-3f4a-5b6c7d8e9f0a",
        "name": "空氣清淨機",
        "description": "有效過濾PM2.5，還你清新空氣。",
        "price": 4990,
        "imageUrl": "https://placehold.co/300x200?text=AirPurifier",
        "tags": ["生活家電", "生活家電"],
        "categoryId": "c3-2",
    },
    {
        "id": "e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b",
        "name": "吸塵器",
        "description": "強大吸力，清潔無死角。",
        "price": 6990,
        "imageUrl": "https://placehold.co/300x200?text=Vacuum",
        "tags": ["生活家電", "清潔"],
        "categoryId": "c3-2",
    },
    {
        "id": "f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c",
        "name": "瑜珈墊",
        "description": "加厚防滑，適合各種瑜珈動作。",
        "price": 690,
        "imageUrl": "https://placehold.co/300x200?text=YogaMat",
        "tags": ["戶外運動", "健身器材"],
        "categoryId": "c5-1",
    },
    {
        "id": "a9b0c1d2-e3f4-4a5b-6c7d-8e9f0a1b2c3d",
        "name": "運動水壺",
        "description": "大容量，耐摔材質。",
        "price": 390,
        "imageUrl": "https://placehold.co/300x200?text=WaterBottle",
        "tags": ["戶外運動", "配件"],
        "categoryId": "c5-1",
    },
    {
        "id": "b0c1d2e3-f4a5-4b6c-7d8e-9f0a1b2c3d4e",
        "name": "簡約風格檯燈",
        "description": "護眼燈光，可調節亮度。",
        "price": 890,
        "imageUrl": "https://placehold.co/300x200?text=Lamp",
        "tags": ["家居生活", "燈具"],
        "categoryId": "c4-1",
    },
    {
        "id": "c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f",
        "name": "人體工學椅",
        "description": "久坐不累，保護脊椎。",
        "price": 5990,
        "imageUrl": "https://placehold.co/300x200?text=Chair",
        "tags": ["家居生活", "辦公家具"],
        "categoryId": "c4-2",
    },
    {
        "id": "d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a",
        "name": "真皮皮帶",
        "description": "經典款式，百搭耐用。",
        "price": 790,
        "imageUrl": "https://placehold.co/300x200?text=Belt",
        "tags": ["流行服飾", "配件"],
        "categoryId": "c2-2",
    },
    {
        "id": "e3f4a5b6-c7d8-4e9f-0a1b-2c3d4e5f6a7b",
        "name": "休閒長褲",
        "description": "舒適修身，適合各種場合。",
        "price": 890,
        "imageUrl": "https://placehold.co/300x200?text=Pants",
        "tags": ["流行服飾", "男裝"],
        "categoryId": "c2-1",
    },
    {
        "id": "f4a5b6c7-d8e9-4f0a-1b2c-3d4e5f6a7b8c",
        "name": "連帽外套",
        "description": "保暖時尚，秋冬必備。",
        "price": 1590,
        "imageUrl": "https://placehold.co/300x200?text=Hoodie",
        "tags": ["流行服飾", "男裝"],
        "categoryId": "c2-1",
    },
    {
        "id": "a5b6c7d8-e9f0-4a1b-2c3d-4e5f6a7b8c9d",
        "name": "藍牙音響",
        "description": "360度環繞音效，防水設計。",
        "price": 2290,
        "imageUrl": "https://placehold.co/300x200?text=Speaker",
        "tags": ["3C 數位", "音響"],
        "categoryId": "c1",
    },
    {
        "id": "b6c7d8e9-f0a1-4b2c-3d4e-5f6a7b8c9d0e",
        "name": "拍立得相機",
        "description": "即拍即得，紀錄美好時刻。",
        "price": 2990,
        "imageUrl": "https://placehold.co/300x200?text=Camera",
        "tags": ["3C 數位", "相機"],
        "categoryId": "c1",
    },
    {
        "id": "c7d8e9f0-a1b2-4c3d-4e5f-6a7b8c9d0e1f",
        "name": "微波爐",
        "description": "快速加熱，方便實用。",
        "price": 2500,
        "imageUrl": "https://placehold.co/300x200?text=Microwave",
        "tags": ["生活家電", "廚房家電"],
        "categoryId": "c3-1",
    },
    {
        "id": "d8e9f0a1-b2c3-4d4e-5f6a-7b8c9d0e1f2a",
        "name": "果汁機",
        "description": "新鮮果汁，健康生活。",
        "price": 1200,
        "imageUrl": "https://placehold.co/300x200?text=Juicer",
        "tags": ["生活家電", "廚房家電"],
        "categoryId": "c3-1",
    },
    {
        "id": "e9f0a1b2-c3d4-4e5f-6a7b-8c9d0e1f2a3b",
        "name": "登山鞋",
        "description": "防水透氣，抓地力強。",
        "price": 3500,
        "imageUrl": "https://placehold.co/300x200?text=HikingShoes",
        "tags": ["流行服飾", "戶外運動"],
        "categoryId": "c5-2",
    },
    {
        "id": "f0a1b2c3-d4e5-4f6a-7b8c-9d0e1f2a3b4c",
        "name": "露營帳篷",
        "description": "輕量化設計，快速搭建。",
        "price": 4500,
        "imageUrl": "https://placehold.co/300x200?text=Tent",
        "tags": ["戶外運動", "露營用品"],
        "categoryId": "c5-2",
    },
    {
        "id": "01b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d",
        "name": "行動電源",
        "description": "大容量，支援快充。",
        "price": 990,
        "imageUrl": "https://placehold.co/300x200?text=PowerBank",
        "tags": ["3C 數位", "手機配件"],
        "categoryId": "c1",
    },
    {
        "id": "12c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e",
        "name": "平板電腦",
        "description": "輕薄便攜，影音娛樂首選。",
        "price": 12900,
        "imageUrl": "https://placehold.co/300x200?text=Tablet",
        "tags": ["3C 數位", "電腦"],
        "categoryId": "c1-3",
    },
]


async def seed_data():
    async with AsyncSessionLocal() as session:
        # 1. Seed Categories
        logger.info("Seeding Categories...")
        for cat_data in MOCK_CATEGORIES:
            stmt = select(CategoryModel).where(CategoryModel.name == cat_data["name"])
            result = await session.execute(stmt)
            existing_cat = result.scalar_one_or_none()

            if not existing_cat:
                new_cat = CategoryModel(
                    id=cat_data["id"], name=cat_data["name"], slug=cat_data["slug"]
                )
                session.add(new_cat)
                logger.info(f"Added Category: {new_cat.name}")
            else:
                logger.info(f"Category already exists: {existing_cat.name}")

        await session.flush()

        # 2. Seed Products
        logger.info("Seeding Products...")
        for prod_data in MOCK_PRODUCTS:
            prod_id = uuid.UUID(prod_data["id"])
            stmt = select(ProductModel).where(ProductModel.id == prod_id)
            result = await session.execute(stmt)
            existing_prod = result.scalar_one_or_none()

            if not existing_prod:
                cat_id_str = prod_data.get("categoryId")
                db_cat_id = CATEGORY_MAPPING.get(str(cat_id_str))

                new_prod = ProductModel(
                    id=prod_id,
                    name=prod_data["name"],
                    description=prod_data["description"],
                    price=prod_data["price"],
                    stock_quantity=100,
                    category_id=db_cat_id,
                    is_active=True,
                )
                session.add(new_prod)

                if "imageUrl" in prod_data:
                    new_image = ProductImageModel(
                        product_id=prod_id, url=prod_data["imageUrl"], is_primary=True
                    )
                    session.add(new_image)

                logger.info(f"Added Product: {new_prod.name}")
            else:
                logger.info(f"Product already exists: {prod_data['name']}")

        await session.commit()
        logger.info("Seeding Completed Successfully!")


if __name__ == "__main__":
    import sys
    import os

    # 支援 Render 環境 (PYTHONPATH=/app/src)
    # 確保當前目錄和 src 目錄都在 path 中
    current_dir = os.path.dirname(os.path.abspath(__file__))
    src_dir = os.path.dirname(current_dir)

    if src_dir not in sys.path:
        sys.path.append(src_dir)

    # 預防萬一：如果是在 backend/ 目錄執行，且 PYTHONPATH 沒設好
    parent_dir = os.path.dirname(src_dir)
    if parent_dir not in sys.path and os.path.basename(src_dir) == "src":
        sys.path.append(parent_dir)

    asyncio.run(seed_data())
