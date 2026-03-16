import pytest
from typing import List
from src.shared.domain.events import DomainEvent
from src.shared.domain.event_bus import IEventBus, EventHandler


class InMemoryEventBus(IEventBus):
    """記憶體實作用於測試"""

    def __init__(self):
        self.published_events: List[DomainEvent] = []
        self.handlers = {}

    async def publish(self, event: DomainEvent) -> None:
        self.published_events.append(event)
        event_type = type(event)
        if event_type in self.handlers:
            for handler in self.handlers[event_type]:
                await handler(event)

    def subscribe(self, event_type, handler: EventHandler) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)


class SampleEvent(DomainEvent):
    message: str


@pytest.mark.asyncio
async def test_event_bus_publish():
    """測試事件發布"""
    bus = InMemoryEventBus()
    event = SampleEvent(message="test")

    await bus.publish(event)

    assert len(bus.published_events) == 1
    assert bus.published_events[0].message == "test"


@pytest.mark.asyncio
async def test_event_bus_subscribe():
    """測試事件訂閱"""
    bus = InMemoryEventBus()
    received_events = []

    async def handler(event: DomainEvent):
        received_events.append(event)

    bus.subscribe(SampleEvent, handler)  # 更新：使用 SampleEvent
    await bus.publish(SampleEvent(message="test"))  # 更新：使用 SampleEvent

    assert len(received_events) == 1
