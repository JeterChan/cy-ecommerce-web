from typing import Protocol, Type, Callable, Awaitable
from .events import DomainEvent

# 定義事件處理器的型別：一個接收 DomainEvent 並回傳 None 的非同步函式
EventHandler = Callable[[DomainEvent], Awaitable[None]]


class IEventBus(Protocol):
    """
    事件匯流排介面 (Interface)
    模組只依賴這個介面, 不依賴具體操作 (ex. Redis/Memory)
    """

    async def publish(self, event: DomainEvent) -> None:
        """發佈事件"""
        ...

    def subscribe(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        """訂閱事件"""
        ...
