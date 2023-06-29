from abc import abstractmethod
from typing import Dict, Any


class Serializable:

  @abstractmethod
  def serialize(self) -> Dict[str, Any]:
    pass

  @staticmethod
  @abstractmethod
  def deserialize(values: Dict[str, Any]):
    pass


# END
