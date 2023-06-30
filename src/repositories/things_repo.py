from typing import Callable, Any

from src.domain.models.thing import Thing
from src.utils.lira import Lira
from src.utils.lira_repo import LiraRepo

T = Thing
Key = int


class ThingsRepo(LiraRepo):
  LIRA_CATEGORY = 'LIRA_THING_CATEGORY'

  def __init__(self, lira: Lira):
    super().__init__(lira, self.LIRA_CATEGORY)

  def valueToSerialized(self, value: T) -> {str: Any}:
    return value.serialize()

  def valueFromSerialized(self, serialized: {str: Any}) -> T:
    return Thing.deserialize(serialized)

  def addValueListener(self, value: T, listener: Callable):
    value.addListener(listener)

  def keyByValue(self, value: T) -> Key:
    return value.article
