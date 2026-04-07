from typing import List, Optional
from modules.product.domain.entities import Product
from modules.product.domain.repository import IProductRepository


class ListProductsUseCase:
    """列出商品清單的業務邏輯"""

    def __init__(self, repo: IProductRepository):
        self.repo = repo

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        category_id: Optional[int] = None,
        category_ids: Optional[List[int]] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[List[Product], int]:
        """
        執行列出商品清單

        Args:
            skip: 略過的筆數
            limit: 取得的筆數上限
            category_id: 分類 ID 篩選 (單選)
            category_ids: 分類 ID 列表篩選 (多選)
            is_active: 是否只顯示上架商品 (None=全部, True=上架, False=下架)

        Returns:
            Tuple[商品 Entity 列表, 總筆數]
        """
        return await self.repo.list(
            skip=skip,
            limit=limit,
            category_id=category_id,
            category_ids=category_ids,
            is_active=is_active,
        )
