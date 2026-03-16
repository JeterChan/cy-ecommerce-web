from typing import List, Optional, Tuple
from modules.product.domain.entities import Product
from modules.product.domain.repository import IProductRepository


class ListProductsAdminUseCase:
    """管理員列出商品清單的業務邏輯（支援搜尋、篩選、排序、分頁）"""

    def __init__(self, repo: IProductRepository):
        self.repo = repo

    async def execute(
        self,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        sort: str = "created_desc",
    ) -> Tuple[List[Product], int]:
        """
        執行管理員商品清單查詢

        Args:
            page: 頁碼（從 1 開始）
            limit: 每頁筆數
            search: 搜尋商品名稱關鍵字
            category_id: 分類 ID 篩選
            sort: 排序方式（created_desc / created_asc）

        Returns:
            (商品 Entity 列表, 總筆數)
        """
        return await self.repo.list_admin(
            page=page,
            limit=limit,
            search=search,
            category_id=category_id,
            sort=sort,
        )
