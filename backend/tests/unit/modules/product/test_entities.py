import pytest
from decimal import Decimal

from modules.product.domain.entities import Product, ProductImage, Category

# ── Product.validate() ──


class TestProductValidate:
    def _make_product(self, **overrides):
        defaults = dict(
            name="測試商品",
            description="商品描述",
            price=Decimal("100.00"),
            stock_quantity=10,
            images=[ProductImage(url="https://example.com/img.jpg", is_primary=True)],
        )
        defaults.update(overrides)
        return Product(**defaults)

    def test_valid_product_passes(self):
        product = self._make_product()
        product.validate()  # should not raise

    def test_empty_name_raises(self):
        product = self._make_product(name="")
        with pytest.raises(ValueError, match="商品名稱不可為空"):
            product.validate()

    def test_whitespace_name_raises(self):
        product = self._make_product(name="   ")
        with pytest.raises(ValueError, match="商品名稱不可為空"):
            product.validate()

    def test_name_too_long_raises(self):
        product = self._make_product(name="a" * 101)
        with pytest.raises(ValueError, match="商品名稱不可超過 100 字元"):
            product.validate()

    def test_price_zero_raises(self):
        product = self._make_product(price=Decimal("0"))
        with pytest.raises(ValueError, match="商品價格必須大於 0"):
            product.validate()

    def test_price_negative_raises(self):
        product = self._make_product(price=Decimal("-1"))
        with pytest.raises(ValueError, match="商品價格必須大於 0"):
            product.validate()

    def test_negative_stock_raises(self):
        product = self._make_product(stock_quantity=-1)
        with pytest.raises(ValueError, match="庫存數量不可為負數"):
            product.validate()

    def test_description_too_long_raises(self):
        product = self._make_product(description="x" * 1001)
        with pytest.raises(ValueError, match="商品描述不可超過 1000 字元"):
            product.validate()

    def test_too_many_images_raises(self):
        images = [
            ProductImage(url=f"https://example.com/{i}.jpg", is_primary=(i == 0))
            for i in range(6)
        ]
        product = self._make_product(images=images)
        with pytest.raises(ValueError, match="每個商品最多只能有 5 張圖片"):
            product.validate()

    def test_no_primary_image_raises(self):
        images = [ProductImage(url="https://example.com/1.jpg", is_primary=False)]
        product = self._make_product(images=images)
        with pytest.raises(ValueError, match="商品必須至少設定一張主圖"):
            product.validate()

    def test_multiple_primary_images_raises(self):
        images = [
            ProductImage(url="https://example.com/1.jpg", is_primary=True),
            ProductImage(url="https://example.com/2.jpg", is_primary=True),
        ]
        product = self._make_product(images=images)
        with pytest.raises(ValueError, match="商品只能有一張主圖"):
            product.validate()

    def test_no_images_passes(self):
        """沒有圖片時不檢查主圖規則"""
        product = self._make_product(images=[])
        product.validate()


# ── Product.update_stock() ──


class TestProductUpdateStock:
    def test_increase_stock(self):
        product = Product(
            name="A", description=None, price=Decimal("10"), stock_quantity=5
        )
        product.update_stock(3)
        assert product.stock_quantity == 8

    def test_decrease_stock_success(self):
        product = Product(
            name="A", description=None, price=Decimal("10"), stock_quantity=5
        )
        product.update_stock(-3)
        assert product.stock_quantity == 2

    def test_decrease_stock_to_zero(self):
        product = Product(
            name="A", description=None, price=Decimal("10"), stock_quantity=5
        )
        product.update_stock(-5)
        assert product.stock_quantity == 0

    def test_decrease_stock_insufficient_raises(self):
        product = Product(
            name="A", description=None, price=Decimal("10"), stock_quantity=2
        )
        with pytest.raises(ValueError, match="庫存不足"):
            product.update_stock(-3)


# ── Category.validate() ──


class TestCategoryValidate:
    def test_valid_category_passes(self):
        cat = Category(id=1, name="電子產品", slug="electronics")
        cat.validate()

    def test_empty_name_raises(self):
        cat = Category(id=1, name="", slug="electronics")
        with pytest.raises(ValueError, match="分類名稱不可為空"):
            cat.validate()

    def test_empty_slug_raises(self):
        cat = Category(id=1, name="電子產品", slug="")
        with pytest.raises(ValueError, match="分類 slug 不可為空"):
            cat.validate()

    def test_uppercase_slug_raises(self):
        cat = Category(id=1, name="電子產品", slug="Electronics")
        with pytest.raises(ValueError, match="分類 slug 必須是小寫且不含空格"):
            cat.validate()

    def test_slug_with_space_raises(self):
        cat = Category(id=1, name="電子產品", slug="my category")
        with pytest.raises(ValueError, match="分類 slug 必須是小寫且不含空格"):
            cat.validate()
