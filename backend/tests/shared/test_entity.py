from datetime import datetime
from src.shared.domain.entity import BaseEntity


def test_entity_auto_generates_id():
    """測試自動生成 ID"""
    entity1 = BaseEntity()
    entity2 = BaseEntity()

    assert entity1.id is not None
    assert entity2.id is not None
    assert entity1.id != entity2.id


def test_entity_auto_generates_timestamps():
    """測試自動生成時間戳"""
    entity = BaseEntity()

    assert isinstance(entity.created_at, datetime)
    assert isinstance(entity.updated_at, datetime)


def test_entity_equality():
    """測試實體相等性比較"""
    entity1 = BaseEntity()
    entity2 = BaseEntity(id=entity1.id)
    entity3 = BaseEntity()

    assert entity1 == entity2  # 相同ID
    assert entity1 != entity3  # 不同ID
    assert entity1 != "not_an_entity"  # 不同型別
