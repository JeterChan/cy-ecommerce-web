import pytest
from decimal import Decimal
from uuid import uuid4

from modules.order.domain.entities import Order, OrderItem


def _make_order_item(**overrides):
    defaults = dict(
        product_id=uuid4(),
        product_name="商品A",
        quantity=2,
        unit_price=Decimal("100.00"),
        subtotal=Decimal("200.00"),
    )
    defaults.update(overrides)
    return OrderItem(**defaults)


def _make_order(items=None, **overrides):
    if items is None:
        items = [_make_order_item()]
    items_total = sum(i.subtotal for i in items)
    defaults = dict(
        user_id=uuid4(),
        order_number="12345678901234561234",
        total_amount=items_total,
        shipping_fee=Decimal("0"),
        status="PENDING",
        recipient_name="王大明",
        recipient_phone="0912345678",
        shipping_address="台北市信義區",
        payment_method="COD",
        items=items,
    )
    defaults.update(overrides)
    return Order(**defaults)


# ── OrderItem.validate() ──


class TestOrderItemValidate:
    def test_valid_item_passes(self):
        item = _make_order_item()
        item.validate()

    def test_quantity_zero_raises(self):
        item = _make_order_item(quantity=0, subtotal=Decimal("0"))
        with pytest.raises(ValueError, match="商品數量必須大於 0"):
            item.validate()

    def test_quantity_negative_raises(self):
        item = _make_order_item(quantity=-1, subtotal=Decimal("-100"))
        with pytest.raises(ValueError, match="商品數量必須大於 0"):
            item.validate()

    def test_subtotal_mismatch_raises(self):
        item = _make_order_item(
            quantity=2, unit_price=Decimal("100"), subtotal=Decimal("999")
        )
        with pytest.raises(ValueError, match="小計金額不正確"):
            item.validate()

    def test_subtotal_arithmetic_correct(self):
        item = _make_order_item(
            quantity=3, unit_price=Decimal("50.50"), subtotal=Decimal("151.50")
        )
        item.validate()


# ── Order.validate() ──


class TestOrderValidate:
    def test_valid_order_passes(self):
        order = _make_order()
        order.validate()

    def test_empty_items_raises(self):
        order = _make_order(items=[], total_amount=Decimal("0"))
        with pytest.raises(ValueError, match="訂單必須至少包含一個商品項目"):
            order.validate()

    def test_total_amount_mismatch_raises(self):
        item = _make_order_item(subtotal=Decimal("200"))
        order = _make_order(
            items=[item],
            total_amount=Decimal("999"),
            shipping_fee=Decimal("0"),
        )
        with pytest.raises(ValueError, match="訂單總金額不正確"):
            order.validate()

    def test_total_includes_shipping_fee(self):
        item = _make_order_item(subtotal=Decimal("200"))
        order = _make_order(
            items=[item],
            total_amount=Decimal("260"),
            shipping_fee=Decimal("60"),
        )
        order.validate()

    def test_multiple_items_total(self):
        item1 = _make_order_item(
            quantity=1, unit_price=Decimal("100"), subtotal=Decimal("100")
        )
        item2 = _make_order_item(
            quantity=3, unit_price=Decimal("50"), subtotal=Decimal("150")
        )
        order = _make_order(
            items=[item1, item2],
            total_amount=Decimal("250"),
            shipping_fee=Decimal("0"),
        )
        order.validate()


# ── Order.calculate_total() ──


class TestOrderCalculateTotal:
    def test_calculate_total_single_item(self):
        item = _make_order_item(subtotal=Decimal("300"))
        order = _make_order(items=[item], shipping_fee=Decimal("60"))
        # Override total_amount so _make_order doesn't set it wrong
        order.total_amount = Decimal("360")
        assert order.calculate_total() == Decimal("360")

    def test_calculate_total_multiple_items(self):
        item1 = _make_order_item(
            quantity=1, unit_price=Decimal("100"), subtotal=Decimal("100")
        )
        item2 = _make_order_item(
            quantity=2, unit_price=Decimal("200"), subtotal=Decimal("400")
        )
        order = _make_order(items=[item1, item2], shipping_fee=Decimal("50"))
        order.total_amount = Decimal("550")
        assert order.calculate_total() == Decimal("550")
