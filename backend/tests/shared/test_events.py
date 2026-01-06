from src.shared.domain.events import DomainEvent


class UserCreatedEvent(DomainEvent):
    user_id: str
    username: str


def test_event_auto_generates_id():
    """測試事件自動生成 ID"""
    event = UserCreatedEvent(user_id="123", username="test")

    assert event.event_id is not None


def test_event_has_occurred_at():
    """測試事件包含發生時間"""
    event = UserCreatedEvent(user_id="123", username="test")

    assert event.occurred_at is not None


def test_event_name_property():
    """測試事件名稱屬性"""
    event = UserCreatedEvent(user_id="123", username="test")

    assert event.event_name == "UserCreatedEvent"
