-- 產品表初始化和種子數據 SQL 腳本
-- 執行方式：psql -h localhost -U user -d ecommerce_db -f init_products.sql

-- 1. 啟用 UUID 擴展（如果尚未啟用）
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. 刪除舊表（如果存在）
DROP TABLE IF EXISTS product_categories CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS categories CASCADE;

-- 3. 創建 products 表（使用 UUID）
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description VARCHAR(1000),
    price NUMERIC(10, 2) NOT NULL,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    category VARCHAR(100),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    image_url VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 4. 創建 categories 表
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    slug VARCHAR(50) NOT NULL UNIQUE
);

-- 5. 創建關聯表
CREATE TABLE product_categories (
    product_id UUID REFERENCES products(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (product_id, category_id)
);

-- 6. 插入產品數據（從前端 mockProducts）
INSERT INTO products (id, name, description, price, stock_quantity, image_url, is_active) VALUES
('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', '智慧型手機 X', '最新的智慧型手機，擁有強大的處理器與相機。', 29900, 100, 'https://placehold.co/300x200?text=Phone', true),
('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', '藍牙耳機 Pro', '主動降噪，高音質無線耳機。', 5990, 200, 'https://placehold.co/300x200?text=Headphone', true),
('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', '純棉T恤', '舒適透氣，百分之百純棉。', 490, 500, 'https://placehold.co/300x200?text=T-Shirt', true),
('d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a', '多功能背包', '防水耐磨，適合旅行與日常使用。', 1290, 300, 'https://placehold.co/300x200?text=Bag', true),
('e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b', '機械鍵盤', '青軸手感，RGB背光。', 2490, 150, 'https://placehold.co/300x200?text=Keyboard', true),
('f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c', '高級咖啡機', '一鍵式操作，享受專業級咖啡。', 8990, 80, 'https://placehold.co/300x200?text=CoffeeMachine', true),
('a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d', '智能手環', '追蹤您的健康與運動數據。', 1590, 250, 'https://placehold.co/300x200?text=SmartBand', true),
('b8c9d0e1-f2a3-4b4c-5d6e-7f8a9b0c1d2e', '無線充電板', '兼容多款手機，快速無線充電。', 790, 300, 'https://placehold.co/300x200?text=WirelessCharger', true),
('c9d0e1f2-a3b4-4c5d-6e7f-8a9b0c1d2e3f', '舒適懶人沙發', '符合人體工學，享受放鬆時光。', 3500, 50, 'https://placehold.co/300x200?text=Sofa', true),
('d0e1f2a3-b4c5-4d6e-7f8a-9b0c1d2e3f4a', '專業運動鞋', '輕量透氣，提供卓越的支撐。', 2800, 200, 'https://placehold.co/300x200?text=Sneakers', true),
('e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b', '多功能電烤箱', '烘焙、燒烤一機搞定。', 4500, 60, 'https://placehold.co/300x200?text=Oven', true),
('f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c', '高質感錢包', '真皮材質，多卡位設計。', 1800, 150, 'https://placehold.co/300x200?text=Wallet', true),
('a3b4c5d6-e7f8-4a9b-0c1d-2e3f4a5b6c7d', '超輕薄筆記型電腦', '強大效能，隨身攜帶。', 35900, 40, 'https://placehold.co/300x200?text=Laptop', true),
('b4c5d6e7-f8a9-4b0c-1d2e-3f4a5b6c7d8e', '電競滑鼠', '高DPI，精準定位。', 1290, 300, 'https://placehold.co/300x200?text=Mouse', true),
('c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f', '抗藍光眼鏡', '保護眼睛，減緩疲勞。', 990, 200, 'https://placehold.co/300x200?text=Glasses', true),
('d6e7f8a9-b0c1-4d2e-3f4a-5b6c7d8e9f0a', '空氣清淨機', '有效過濾PM2.5，還你清新空氣。', 4990, 80, 'https://placehold.co/300x200?text=AirPurifier', true),
('e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b', '吸塵器', '強大吸力，清潔無死角。', 6990, 70, 'https://placehold.co/300x200?text=Vacuum', true),
('f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c', '瑜珈墊', '加厚防滑，適合各種瑜珈動作。', 690, 400, 'https://placehold.co/300x200?text=YogaMat', true),
('a9b0c1d2-e3f4-4a5b-6c7d-8e9f0a1b2c3d', '運動水壺', '大容量，耐摔材質。', 390, 500, 'https://placehold.co/300x200?text=WaterBottle', true),
('b0c1d2e3-f4a5-4b6c-7d8e-9f0a1b2c3d4e', '簡約風格檯燈', '護眼燈光，可調節亮度。', 890, 150, 'https://placehold.co/300x200?text=Lamp', true),
('c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f', '人體工學椅', '久坐不累，保護脊椎。', 5990, 60, 'https://placehold.co/300x200?text=Chair', true),
('d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a', '真皮皮帶', '經典款式，百搭耐用。', 790, 200, 'https://placehold.co/300x200?text=Belt', true),
('e3f4a5b6-c7d8-4e9f-0a1b-2c3d4e5f6a7b', '休閒長褲', '舒適修身，適合各種場合。', 890, 300, 'https://placehold.co/300x200?text=Pants', true),
('f4a5b6c7-d8e9-4f0a-1b2c-3d4e5f6a7b8c', '連帽外套', '保暖時尚，秋冬必備。', 1590, 250, 'https://placehold.co/300x200?text=Hoodie', true),
('a5b6c7d8-e9f0-4a1b-2c3d-4e5f6a7b8c9d', '藍牙音響', '360度環繞音效，防水設計。', 2290, 120, 'https://placehold.co/300x200?text=Speaker', true),
('b6c7d8e9-f0a1-4b2c-3d4e-5f6a7b8c9d0e', '拍立得相機', '即拍即得，紀錄美好時刻。', 2990, 90, 'https://placehold.co/300x200?text=Camera', true),
('c7d8e9f0-a1b2-4c3d-4e5f-6a7b8c9d0e1f', '微波爐', '快速加熱，方便實用。', 2500, 100, 'https://placehold.co/300x200?text=Microwave', true),
('d8e9f0a1-b2c3-4d4e-5f6a-7b8c9d0e1f2a', '果汁機', '新鮮果汁，健康生活。', 1200, 150, 'https://placehold.co/300x200?text=Juicer', true),
('e9f0a1b2-c3d4-4e5f-6a7b-8c9d0e1f2a3b', '登山鞋', '防水透氣，抓地力強。', 3500, 100, 'https://placehold.co/300x200?text=HikingShoes', true),
('f0a1b2c3-d4e5-4f6a-7b8c-9d0e1f2a3b4c', '露營帳篷', '輕量化設計，快速搭建。', 4500, 50, 'https://placehold.co/300x200?text=Tent', true),
('01b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', '行動電源', '大容量，支援快充。', 990, 400, 'https://placehold.co/300x200?text=PowerBank', true),
('12c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', '平板電腦', '輕薄便攜，影音娛樂首選。', 12900, 80, 'https://placehold.co/300x200?text=Tablet', true);

-- 7. 驗證數據
SELECT COUNT(*) as total_products FROM products;
SELECT id, name, price, stock_quantity FROM products LIMIT 5;

-- 完成！
SELECT '✅ 產品表初始化完成！共插入 ' || COUNT(*) || ' 個產品' as result FROM products;

