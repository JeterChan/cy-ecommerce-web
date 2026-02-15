"""
Cart API Routes

定義 Cart 模組的 HTTP API 端點

注意：Cart 模組的 API 尚未完整實作
此檔案僅提供基本結構，待 Use Cases 完成後再實作
"""
from fastapi import APIRouter

router = APIRouter(prefix="/cart", tags=["Cart"])


# TODO: 實作 Cart API 端點
#
# 建議的端點：
# - POST /cart/items - 新增購物車項目
# - GET /cart - 取得購物車
# - GET /cart/items - 列出購物車項目
# - PUT /cart/items/{id} - 更新購物車項目
# - DELETE /cart/items/{id} - 刪除購物車項目
# - DELETE /cart - 清空購物車


@router.get("/")
async def get_cart_placeholder():
    """
    取得購物車（佔位符）

    待實作完整的 Use Case 後再實作此端點
    """
    return {
        "message": "Cart API - 待實作",
        "status": "placeholder"
    }

