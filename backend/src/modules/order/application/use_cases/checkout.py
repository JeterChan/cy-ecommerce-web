from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from uuid import UUID
from typing import List, Dict, Optional, TYPE_CHECKING
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

from modules.order.domain.exceptions import (
    InsufficientStockException,
    EmptyCartException
)
from modules.order.domain.repository import IOrderRepository, ICartAdapter
from modules.order.domain.entities import Order, OrderItem
from modules.order.domain.value_objects import OrderStatus
from modules.order.application.dtos.checkout_request import CheckoutRequest
from modules.order.application.dtos.order_response import OrderResponse
from modules.order.application.dtos.order_item_response import OrderItemResponse

if TYPE_CHECKING:
    from infrastructure.stock_redis_service import StockRedisService

# Assuming these exist in other modules
from modules.product.infrastructure.models import ProductModel

class CheckoutUseCase:
    def __init__(
        self,
        db: AsyncSession,
        order_repo: IOrderRepository,
        cart_repo,
        product_repo,
        stock_service: Optional["StockRedisService"] = None,
    ):
        self.db = db
        self.order_repo = order_repo
        self.cart_repo = cart_repo
        self.product_repo = product_repo
        self.stock_service = stock_service

    async def execute(self, user_id: UUID, request: CheckoutRequest) -> OrderResponse:
        """
        執行原子結帳流程
        """
        owner_id = str(user_id)

        # 1. 讀取 Redis 購物車 (外部操作，不需要在 DB 事務內)
        if hasattr(self.cart_repo, 'get_cart'):
            cart_items = await self.cart_repo.get_cart(owner_id)
        else:
            cart_items = await self.cart_repo.get_cart_items(owner_id)

        if not cart_items:
            raise EmptyCartException()

        # 2. Redis 預扣庫存：在進入 DB 事務之前過濾庫存不足的請求
        deducted_items: List[tuple] = []  # [(product_id, quantity), ...]
        if self.stock_service:
            try:
                for item in cart_items:
                    success, _ = await self.stock_service.try_deduct(item.product_id, item.quantity)
                    if not success:
                        # 回滾所有已成功預扣的商品
                        for pid, qty in deducted_items:
                            await self.stock_service.rollback(pid, qty)
                        raise InsufficientStockException(
                            product_name=str(item.product_id),
                            requested=item.quantity,
                            available=0,
                        )
                    deducted_items.append((item.product_id, item.quantity))
            except InsufficientStockException:
                raise
            except Exception:
                # Redis 異常：回滾已預扣的，然後重新拋出
                for pid, qty in deducted_items:
                    await self.stock_service.rollback(pid, qty)
                raise

        # 3. 執行資料庫原子操作，實作重試機制以應對極低機率的訂單編號碰撞
        max_retries = 3
        last_err = None
        created_order = None
        try:
            for attempt in range(max_retries):
                try:
                    if not self.db.in_transaction():
                        async with self.db.begin():
                            created_order = await self._perform_checkout(user_id, cart_items, request)
                    else:
                        created_order = await self._perform_checkout(user_id, cart_items, request)
                        await self.db.flush()
                    break
                except IntegrityError as e:
                    last_err = e
                    if "order_number" in str(e).lower() and not self.db.in_transaction() and attempt < max_retries - 1:
                        logger.warning(f"訂單編號碰撞 (attempt {attempt + 1}), 正在重新產生並重試...")
                        await self.db.rollback()
                        continue
                    raise e

            if created_order is None and last_err:
                raise last_err
        except Exception:
            # DB 事務失敗：回滾 Redis 預扣的庫存
            if self.stock_service:
                for pid, qty in deducted_items:
                    await self.stock_service.rollback(pid, qty)
            raise

        # 4. 成功提交後清空 Redis 購物車
        await self.cart_repo.clear_cart(owner_id)

        # 5. 轉換為 Response DTO
        return OrderResponse.model_validate(created_order)

    async def _perform_checkout(self, user_id: UUID, cart_items: list, request: CheckoutRequest) -> Order:
        """
        在資料庫事務內執行的核心結帳邏輯
        """
        product_ids = [item.product_id for item in cart_items]

        # 悲觀鎖定 (FOR UPDATE) 相關商品，並按照 ID 排序防止死鎖
        stmt = select(ProductModel).where(ProductModel.id.in_(product_ids)).with_for_update(of=ProductModel).order_by(ProductModel.id)
        res = await self.db.execute(stmt)
        products = res.scalars().all()
        product_map = {p.id: p for p in products}

        # 建立購物車項目映射表，方便後續查找名稱
        cart_item_map = {item.product_id: item for item in cart_items}

        # 驗證所有商品是否存在且上架
        for pid in product_ids:
            if pid not in product_map or not product_map[pid].is_active:
                # 嘗試從購物車項目中獲取名稱，避免顯示 UUID
                item = cart_item_map.get(pid)
                product_name = getattr(item, 'name', '未知商品') if item else '未知商品'
                raise ValueError(f"商品 '{product_name}' 不存在或已下架，請重新確認購物車")

        total_amount = Decimal("0.0")
        order_items = []

        # 驗證並扣除庫存
        for item in cart_items:
            product_model = product_map[item.product_id]

            if product_model.stock_quantity < item.quantity:
                raise InsufficientStockException(
                    product_name=product_model.name,
                    requested=item.quantity,
                    available=product_model.stock_quantity
                )
            
            item_total = Decimal(str(product_model.price)) * item.quantity
            total_amount += item_total

            # 扣除庫存 (直接修改 Model)
            product_model.stock_quantity -= item.quantity
            self.db.add(product_model)

            order_items.append(
                OrderItem(
                    product_id=product_model.id,
                    product_name=product_model.name,
                    quantity=item.quantity,
                    unit_price=Decimal(str(product_model.price)),
                    subtotal=item_total
                )
            )

        # 建立訂單領域實體
        order_number = self._generate_order_number(user_id)
        order = Order(
            user_id=user_id,
            order_number=order_number,
            total_amount=total_amount,
            shipping_fee=Decimal("0.0"), # MVP 暫定 0
            status=OrderStatus.PENDING.value,
            recipient_name=request.recipient_name,
            recipient_phone=request.recipient_phone,
            shipping_address=request.shipping_address,
            payment_method=request.payment_method,
            note=request.note,
            items=order_items
        )
        
        return await self.order_repo.create(order)

    def _generate_order_number(self, user_id: UUID) -> str:
        """
        產生純數字訂單編號：YYMMDDHHMMSS + 微秒後4位 + 使用者ID數字末4位
        這種格式確保了同一使用者在同一微秒內幾乎不會產生重複編號。
        總長度為 20 位 (12 + 4 + 4)，符合資料庫 String(20) 限制。
        """
        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%y%m%d%H%M%S") # 12位
        micro_str = now.strftime("%f")[:4]      # 取微秒前4位
        
        # 獲取 UUID 中的數字部分並取末 4 位
        user_num_str = "".join(filter(str.isdigit, str(user_id)))[-4:].zfill(4)
        
        return f"{date_str}{micro_str}{user_num_str}"
