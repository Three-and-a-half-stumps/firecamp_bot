from typing import Dict, Any

from src.utils.serializable import Serializable


class DailyInfoTime(Serializable):

  def serialize(self) -> Dict[str, Any]:
    return {
      'hours': self.hours,
      'minutes': self.minutes,
    }

  @staticmethod
  def deserialize(values: Dict[str, Any]):
    return DailyInfoTime(
      hours=values['hours'],
      minutes=values['minutes'],
    )

  def __init__(self, hours: int, minutes: int):
    self.hours = hours
    self.minutes = minutes
