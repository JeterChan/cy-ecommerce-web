"""
Order Module - Use Case: Create Order

建立訂單用例。
"""

from decimal import Decimal
from typing import List
from uuid import UUID
from modules.order.domain.entities import Order, OrderItem
from modules.order.domain.value_objects import OrderStatus
from modules.order.domain.repository import IOrderRepository
from modules.order.infrastructure.repositories.redis_cart_repository import OrderCartAdapter
from modules.product.domain.repository import ProductRepository
from modules.cart.domain.schemas import CartItemResponse
from shared.exceptions import BusinessRuleViolationException, ResourceNotFoundException


class CreateOrderItemInput:
    """建立訂單項目的輸入資料"""
    def __init__(self, product_id: UUID, quantity: int):
        self.product_id = product_id
        self.quantity = quantity


class CreateOrderUseCase:
    """建立訂單用例"""

    def __init__(
        self,
        order_repository: IOrderRepository,
        cart_adapter: OrderCartAdapter,
        product_repository: ProductRepository
    ):
        """
        初始化用例

        Args:
            order_repository: 訂單 Repository
            cart_adapter: 購物車適配器
            product_repository: 商品 Repository
        """
        self.order_repo = order_repository
        self.cart_adapter = cart_adapter
        self.product_repo = product_repository

    async def execute(
        self,
        user_id: str,
        items: List[CreateOrderItemInput],
        shipping_fee: Decimal = Decimal("60.00"),
        note: str | None = None
    ) -> Order:
        """
        執行建立訂單流程

        流程：
        1. 驗證商品列表不為空
        2. 查詢商品資訊並建立訂單項目（價格快照）
        3. 計算訂單總金額
        4. 建立訂單實體並驗證
        5. 儲存訂單至資料庫
        6. （可選）清空購物車

        Args:
            user_id: 使用者 ID
            items: 訂單商品列表（從前端傳遞）
            shipping_fee: 運費（預設 60 元）
            note: 訂單備註

        Returns:
            Order: 建立完成的訂單

        Raises:
            BusinessRuleViolationException: 商品列表為空或業務規則驗證失敗
            ResourceNotFoundException: 商品不存在
        """
        print(f"\n{'='*60}")
        print(f"🛍️ [CreateOrder UseCase] 開始建立訂單")
        print(f"👤 [CreateOrder UseCase] 使用者 ID: {user_id}")
        print(f"📦 [CreateOrder UseCase] 前端傳遞商品數量: {len(items)}")
        print(f"🚚 [CreateOrder UseCase] 運費: {shipping_fee}")
        print(f"📝 [CreateOrder UseCase] 備註: {note or '無'}")
        print(f"{'='*60}\n")

        # 1. 驗證商品列表不為空
        print(f"🔍 [CreateOrder UseCase] 步驟 1: 驗證商品列表...")
        if not items or len(items) == 0:
            print(f"❌ [CreateOrder UseCase] 商品列表為空，無法建立訂單")
            raise BusinessRuleViolationException("商品列表為空，無法建立訂單")

        print(f"✅ [CreateOrder UseCase] 商品列表驗證通過，共 {len(items)} 個商品")
        for idx, item in enumerate(items, 1):
            print(f"   {idx}. 商品 ID: {item.product_id}, 數量: {item.quantity}")

        # 2. 建立訂單項目（價格快照）
        print(f"\n🔍 [CreateOrder UseCase] 步驟 2: 查詢商品資訊並建立訂單項目...")
        order_items = await self._create_order_items_from_request(items)
        print(f"✅ [CreateOrder UseCase] 成功建立 {len(order_items)} 個訂單項目")

        for idx, item in enumerate(order_items, 1):
            print(f"   {idx}. {item.product_name} - 單價: {item.unit_price}, 數量: {item.quantity}, 小計: {item.subtotal}")

        # 3. 計算訂單總金額
        print(f"\n🔍 [CreateOrder UseCase] 步驟 3: 計算訂單總金額...")
        items_total = sum(item.subtotal for item in order_items)
        total_amount = items_total + shipping_fee
        print(f"💰 [CreateOrder UseCase] 商品小計: {items_total}")
        print(f"🚚 [CreateOrder UseCase] 運費: {shipping_fee}")
        print(f"💰 [CreateOrder UseCase] 訂單總額: {total_amount}")

        # 4. 建立訂單實體
        print(f"\n🔍 [CreateOrder UseCase] 步驟 4: 建立訂單實體...")
        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING.value,
            total_amount=total_amount,
            shipping_fee=shipping_fee,
            note=note,
            items=order_items
        )

        # 驗證訂單
        print(f"✔️ [CreateOrder UseCase] 驗證訂單...")
        order.validate()
        print(f"✅ [CreateOrder UseCase] 訂單驗證通過")

        # 5. 儲存訂單至資料庫（事務）
        print(f"\n🔍 [CreateOrder UseCase] 步驟 5: 儲存訂單至資料庫...")
        created_order = await self.order_repo.create(order)
        print(f"✅ [CreateOrder UseCase] 訂單已儲存，訂單 ID: {created_order.id}")

        # 6. （可選）清空購物車
        print(f"\n🔍 [CreateOrder UseCase] 步驟 6: 清空購物車（會員才需要）...")
        try:
            await self.cart_adapter.clear_cart(user_id)
            print(f"✅ [CreateOrder UseCase] 購物車已清空")
        except Exception as e:
            # 清空購物車失敗不影響訂單建立
            print(f"⚠️ [CreateOrder UseCase] 清空購物車失敗（可能是訪客）: {e}")

        print(f"\n✨ [CreateOrder UseCase] 訂單建立完成！")
        print(f"{'='*60}\n")

        return created_order

    async def _create_order_items_from_request(
        self,
        items: List[CreateOrderItemInput]
    ) -> List[OrderItem]:
        """
        根據前端傳遞的商品列表建立訂單項目（含價格快照）

        Args:
            items: 前端傳遞的商品列表

        Returns:
            List[OrderItem]: 訂單項目列表

        Raises:
            ResourceNotFoundException: 商品不存在
        """
        print(f"\n   📋 [_create_order_items_from_request] 開始處理 {len(items)} 個商品...")
        order_items = []

        for idx, item_input in enumerate(items, 1):
            print(f"\n   🔍 [{idx}/{len(items)}] 處理商品...")
            print(f"      商品 ID: {item_input.product_id}")
            print(f"      數量: {item_input.quantity}")

            # 查詢商品以取得當前價格（價格快照）
            print(f"      🔍 查詢商品資料...")
            product = await self.product_repo.get_by_id(item_input.product_id)

            if product is None:
                print(f"      ❌ 商品不存在: {item_input.product_id}")
                raise ResourceNotFoundException(
                    f"商品 {item_input.product_id} 不存在"
                )

            print(f"      ✅ 找到商品: {product.name}")
            print(f"      💰 商品價格: {product.price}")

            # 建立訂單項目（價格快照）
            unit_price = Decimal(str(product.price))
            quantity = item_input.quantity
            subtotal = unit_price * quantity

            print(f"      📊 計算: {unit_price} × {quantity} = {subtotal}")

            order_item = OrderItem(
                product_id=item_input.product_id,
                product_name=product.name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )

            order_items.append(order_item)
            print(f"      ✅ 訂單項目已建立")

        print(f"\n   ✨ [_create_order_items_from_request] 完成！共建立 {len(order_items)} 個訂單項目\n")
        return order_items

    async def _create_order_items(
        self,
        cart_items: List[CartItemResponse]
    ) -> List[OrderItem]:
        """
        根據購物車項目建立訂單項目（含價格快照）

        Args:
            cart_items: 購物車項目列表

        Returns:
            List[OrderItem]: 訂單項目列表

        Raises:
            ResourceNotFoundException: 商品不存在
        """
        print(f"\n   📋 [_create_order_items] 開始處理 {len(cart_items)} 個購物車項目...")
        order_items = []

        for idx, cart_item in enumerate(cart_items, 1):
            print(f"\n   🔍 [{idx}/{len(cart_items)}] 處理購物車項目...")
            print(f"      商品 ID (購物車): {cart_item.product_id}")
            print(f"      數量: {cart_item.quantity}")

            # Cart 使用 UUID，Product 可能使用 UUID 或 int
            # 嘗試將 UUID 轉換為適當格式
            try:
                # 如果 product_id 已經是 UUID，直接使用
                from uuid import UUID
                if isinstance(cart_item.product_id, UUID):
                    product_id = cart_item.product_id
                    print(f"      商品 ID (UUID): {product_id}")
                else:
                    # 如果是字串，嘗試轉換為 UUID
                    product_id = UUID(str(cart_item.product_id))
                    print(f"      商品 ID (轉換為 UUID): {product_id}")
            except (ValueError, AttributeError) as e:
                print(f"      ❌ 無效的商品 ID 格式: {cart_item.product_id}, 錯誤: {e}")
                raise BusinessRuleViolationException(
                    f"無效的商品 ID 格式: {cart_item.product_id}"
                )

            # 查詢商品以取得當前價格（價格快照）
            print(f"      🔍 查詢商品資料...")
            product = await self.product_repo.get_by_id(product_id)

            if product is None:
                print(f"      ❌ 商品不存在: {product_id}")
                raise ResourceNotFoundException(
                    f"商品 {product_id} 不存在"
                )

            print(f"      ✅ 找到商品: {product.name}")
            print(f"      💰 商品價格: {product.price}")

            # 建立訂單項目（價格快照）
            unit_price = Decimal(str(product.price))
            quantity = cart_item.quantity
            subtotal = unit_price * quantity

            print(f"      📊 計算: {unit_price} × {quantity} = {subtotal}")

            order_item = OrderItem(
                product_id=product_id,
                product_name=product.name,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=subtotal
            )

            order_items.append(order_item)
            print(f"      ✅ 訂單項目已建立")

        print(f"\n   ✨ [_create_order_items] 完成！共建立 {len(order_items)} 個訂單項目\n")
        return order_items


