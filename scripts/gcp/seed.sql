-- =============================================================================
-- seed.sql — 初始假資料匯入
--
-- 用途：匯入分類、商品、商品圖片的測試資料
-- 執行方式：
--   1. Cloud SQL Studio：複製貼上此檔案內容執行
--   2. gcloud sql connect：
--        gcloud sql connect cy-ecommerce-db --user=ecommerce_user --database=ecommerce
--        \i seed.sql
-- 重複執行安全（ON CONFLICT DO NOTHING）
-- =============================================================================

-- 插入分類
INSERT INTO categories (id, name, slug) VALUES
  (1, '3C 數位', 'digital-3c'),
  (2, '流行服飾', 'fashion'),
  (3, '生活家電', 'appliances'),
  (4, '家居生活', 'home-living'),
  (5, '戶外運動', 'outdoor-sports')
ON CONFLICT DO NOTHING;

-- 插入商品
INSERT INTO products (id, name, description, price, stock_quantity, category_id, is_active) VALUES
  ('a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', '智慧型手機 X',     '最新的智慧型手機，擁有強大的處理器與相機。', 29900, 100, 1, true),
  ('b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', '藍牙耳機 Pro',     '主動降噪，高音質無線耳機。',               5990,  100, 1, true),
  ('c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', '純棉T恤',          '舒適透氣，百分之百純棉。',                   490,   100, 2, true),
  ('d4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a', '多功能背包',        '防水耐磨，適合旅行與日常使用。',             1290,  100, 2, true),
  ('e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b', '機械鍵盤',          '青軸手感，RGB背光。',                       2490,  100, 1, true),
  ('f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c', '高級咖啡機',        '一鍵式操作，享受專業級咖啡。',               8990,  100, 3, true),
  ('a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d', '智能手環',          '追蹤您的健康與運動數據。',                   1590,  100, 1, true),
  ('b8c9d0e1-f2a3-4b4c-5d6e-7f8a9b0c1d2e', '無線充電板',        '兼容多款手機，快速無線充電。',                790,   100, 1, true),
  ('c9d0e1f2-a3b4-4c5d-6e7f-8a9b0c1d2e3f', '舒適懶人沙發',      '符合人體工學，享受放鬆時光。',               3500,  100, 4, true),
  ('d0e1f2a3-b4c5-4d6e-7f8a-9b0c1d2e3f4a', '專業運動鞋',        '輕量透氣，提供卓越的支撐。',                 2800,  100, 2, true),
  ('e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b', '多功能電烤箱',      '烘焙、燒烤一機搞定。',                       4500,  100, 3, true),
  ('f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c', '高質感錢包',        '真皮材質，多卡位設計。',                     1800,  100, 2, true),
  ('a3b4c5d6-e7f8-4a9b-0c1d-2e3f4a5b6c7d', '超輕薄筆記型電腦',  '強大效能，隨身攜帶。',                      35900, 100, 1, true),
  ('b4c5d6e7-f8a9-4b0c-1d2e-3f4a5b6c7d8e', '電競滑鼠',          '高DPI，精準定位。',                          1290,  100, 1, true),
  ('c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f', '抗藍光眼鏡',        '保護眼睛，減緩疲勞。',                        990,   100, 2, true),
  ('d6e7f8a9-b0c1-4d2e-3f4a-5b6c7d8e9f0a', '空氣清淨機',        '有效過濾PM2.5，還你清新空氣。',              4990,  100, 3, true),
  ('e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b', '吸塵器',            '強大吸力，清潔無死角。',                     6990,  100, 3, true),
  ('f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c', '瑜珈墊',            '加厚防滑，適合各種瑜珈動作。',                690,   100, 5, true),
  ('a9b0c1d2-e3f4-4a5b-6c7d-8e9f0a1b2c3d', '運動水壺',          '大容量，耐摔材質。',                          390,   100, 5, true),
  ('b0c1d2e3-f4a5-4b6c-7d8e-9f0a1b2c3d4e', '簡約風格檯燈',      '護眼燈光，可調節亮度。',                      890,   100, 4, true),
  ('c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f', '人體工學椅',        '久坐不累，保護脊椎。',                       5990,  100, 4, true),
  ('d2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a', '真皮皮帶',          '經典款式，百搭耐用。',                        790,   100, 2, true),
  ('e3f4a5b6-c7d8-4e9f-0a1b-2c3d4e5f6a7b', '休閒長褲',          '舒適修身，適合各種場合。',                    890,   100, 2, true),
  ('f4a5b6c7-d8e9-4f0a-1b2c-3d4e5f6a7b8c', '連帽外套',          '保暖時尚，秋冬必備。',                       1590,  100, 2, true),
  ('a5b6c7d8-e9f0-4a1b-2c3d-4e5f6a7b8c9d', '藍牙音響',          '360度環繞音效，防水設計。',                  2290,  100, 1, true),
  ('b6c7d8e9-f0a1-4b2c-3d4e-5f6a7b8c9d0e', '拍立得相機',        '即拍即得，紀錄美好時刻。',                   2990,  100, 1, true),
  ('c7d8e9f0-a1b2-4c3d-4e5f-6a7b8c9d0e1f', '微波爐',            '快速加熱，方便實用。',                       2500,  100, 3, true),
  ('d8e9f0a1-b2c3-4d4e-5f6a-7b8c9d0e1f2a', '果汁機',            '新鮮果汁，健康生活。',                       1200,  100, 3, true),
  ('e9f0a1b2-c3d4-4e5f-6a7b-8c9d0e1f2a3b', '登山鞋',            '防水透氣，抓地力強。',                       3500,  100, 5, true),
  ('f0a1b2c3-d4e5-4f6a-7b8c-9d0e1f2a3b4c', '露營帳篷',          '輕量化設計，快速搭建。',                     4500,  100, 5, true),
  ('01b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', '行動電源',          '大容量，支援快充。',                          990,   100, 1, true),
  ('12c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', '平板電腦',          '輕薄便攜，影音娛樂首選。',                  12900, 100, 1, true)
ON CONFLICT DO NOTHING;

-- 插入商品圖片（id 為 UUID，SQL 層無預設值需手動提供）
INSERT INTO product_images (id, product_id, url, is_primary) VALUES
  (gen_random_uuid(), 'a1b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'https://placehold.co/300x200?text=Phone',          true),
  (gen_random_uuid(), 'b2c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'https://placehold.co/300x200?text=Headphone',       true),
  (gen_random_uuid(), 'c3d4e5f6-a7b8-4c9d-0e1f-2a3b4c5d6e7f', 'https://placehold.co/300x200?text=T-Shirt',         true),
  (gen_random_uuid(), 'd4e5f6a7-b8c9-4d0e-1f2a-3b4c5d6e7f8a', 'https://placehold.co/300x200?text=Bag',             true),
  (gen_random_uuid(), 'e5f6a7b8-c9d0-4e1f-2a3b-4c5d6e7f8a9b', 'https://placehold.co/300x200?text=Keyboard',        true),
  (gen_random_uuid(), 'f6a7b8c9-d0e1-4f2a-3b4c-5d6e7f8a9b0c', 'https://placehold.co/300x200?text=CoffeeMachine',   true),
  (gen_random_uuid(), 'a7b8c9d0-e1f2-4a3b-4c5d-6e7f8a9b0c1d', 'https://placehold.co/300x200?text=SmartBand',       true),
  (gen_random_uuid(), 'b8c9d0e1-f2a3-4b4c-5d6e-7f8a9b0c1d2e', 'https://placehold.co/300x200?text=WirelessCharger', true),
  (gen_random_uuid(), 'c9d0e1f2-a3b4-4c5d-6e7f-8a9b0c1d2e3f', 'https://placehold.co/300x200?text=Sofa',            true),
  (gen_random_uuid(), 'd0e1f2a3-b4c5-4d6e-7f8a-9b0c1d2e3f4a', 'https://placehold.co/300x200?text=Sneakers',        true),
  (gen_random_uuid(), 'e1f2a3b4-c5d6-4e7f-8a9b-0c1d2e3f4a5b', 'https://placehold.co/300x200?text=Oven',            true),
  (gen_random_uuid(), 'f2a3b4c5-d6e7-4f8a-9b0c-1d2e3f4a5b6c', 'https://placehold.co/300x200?text=Wallet',          true),
  (gen_random_uuid(), 'a3b4c5d6-e7f8-4a9b-0c1d-2e3f4a5b6c7d', 'https://placehold.co/300x200?text=Laptop',          true),
  (gen_random_uuid(), 'b4c5d6e7-f8a9-4b0c-1d2e-3f4a5b6c7d8e', 'https://placehold.co/300x200?text=Mouse',           true),
  (gen_random_uuid(), 'c5d6e7f8-a9b0-4c1d-2e3f-4a5b6c7d8e9f', 'https://placehold.co/300x200?text=Glasses',         true),
  (gen_random_uuid(), 'd6e7f8a9-b0c1-4d2e-3f4a-5b6c7d8e9f0a', 'https://placehold.co/300x200?text=AirPurifier',     true),
  (gen_random_uuid(), 'e7f8a9b0-c1d2-4e3f-4a5b-6c7d8e9f0a1b', 'https://placehold.co/300x200?text=Vacuum',          true),
  (gen_random_uuid(), 'f8a9b0c1-d2e3-4f4a-5b6c-7d8e9f0a1b2c', 'https://placehold.co/300x200?text=YogaMat',         true),
  (gen_random_uuid(), 'a9b0c1d2-e3f4-4a5b-6c7d-8e9f0a1b2c3d', 'https://placehold.co/300x200?text=WaterBottle',     true),
  (gen_random_uuid(), 'b0c1d2e3-f4a5-4b6c-7d8e-9f0a1b2c3d4e', 'https://placehold.co/300x200?text=Lamp',            true),
  (gen_random_uuid(), 'c1d2e3f4-a5b6-4c7d-8e9f-0a1b2c3d4e5f', 'https://placehold.co/300x200?text=Chair',           true),
  (gen_random_uuid(), 'd2e3f4a5-b6c7-4d8e-9f0a-1b2c3d4e5f6a', 'https://placehold.co/300x200?text=Belt',            true),
  (gen_random_uuid(), 'e3f4a5b6-c7d8-4e9f-0a1b-2c3d4e5f6a7b', 'https://placehold.co/300x200?text=Pants',           true),
  (gen_random_uuid(), 'f4a5b6c7-d8e9-4f0a-1b2c-3d4e5f6a7b8c', 'https://placehold.co/300x200?text=Hoodie',          true),
  (gen_random_uuid(), 'a5b6c7d8-e9f0-4a1b-2c3d-4e5f6a7b8c9d', 'https://placehold.co/300x200?text=Speaker',         true),
  (gen_random_uuid(), 'b6c7d8e9-f0a1-4b2c-3d4e-5f6a7b8c9d0e', 'https://placehold.co/300x200?text=Camera',          true),
  (gen_random_uuid(), 'c7d8e9f0-a1b2-4c3d-4e5f-6a7b8c9d0e1f', 'https://placehold.co/300x200?text=Microwave',       true),
  (gen_random_uuid(), 'd8e9f0a1-b2c3-4d4e-5f6a-7b8c9d0e1f2a', 'https://placehold.co/300x200?text=Juicer',          true),
  (gen_random_uuid(), 'e9f0a1b2-c3d4-4e5f-6a7b-8c9d0e1f2a3b', 'https://placehold.co/300x200?text=HikingShoes',     true),
  (gen_random_uuid(), 'f0a1b2c3-d4e5-4f6a-7b8c-9d0e1f2a3b4c', 'https://placehold.co/300x200?text=Tent',            true),
  (gen_random_uuid(), '01b2c3d4-e5f6-4a7b-8c9d-0e1f2a3b4c5d', 'https://placehold.co/300x200?text=PowerBank',       true),
  (gen_random_uuid(), '12c3d4e5-f6a7-4b8c-9d0e-1f2a3b4c5d6e', 'https://placehold.co/300x200?text=Tablet',          true)
ON CONFLICT DO NOTHING;
