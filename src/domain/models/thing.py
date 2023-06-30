import datetime as dt

from typing import Optional, Dict, Any

from src.utils.notifier import Notifier
from src.utils.serializable import Serializable


class Category:
  UP = 'Верх'
  DOWN = 'Низ'
  FULL = 'Костюм'
  SHOES = 'Обувь'
  ACCESSORIES = 'Аксессуары'
  BOOKS = 'Книги'
  OTHER = 'Другое'

  @staticmethod
  def getList() -> [str]:
    return [
      Category.UP,
      Category.DOWN,
      Category.FULL,
      Category.SHOES,
      Category.ACCESSORIES,
      Category.BOOKS,
      Category.OTHER,
    ]


class Price(Serializable):

  def serialize(self) -> Dict[str, Any]:
    return {
      'type': self.type,
      'fixedPrice': self.fixedPrice,
    }

  @staticmethod
  def deserialize(values: Dict[str, Any]):
    return Price(
      type=values['type'],
      fixedPrice=values.get('fixedPrice'),
    )

  FREE = 'FREE'  # свободная цена (сколько угодно)
  DEFAULT_FIXED = 'DEFAULT_FIXED'  # минимум 600 рублей (на платном рейле)
  FIXED = 'FIXED'  # экстравагантные случаи вроде Серёги

  def __init__(self, type: str, fixedPrice: Optional[int] = None):
    self.type = type
    self.fixedPrice = fixedPrice

  def __eq__(self, other):
    if not isinstance(other, Price):
      return False
    return (self.type == other.type and (not self.type == Price.FIXED or
                                         self.fixedPrice == other.fixedPrice))


class Thing(Serializable, Notifier):

  def serialize(self) -> Dict[str, Any]:
    return {
      'article': self.article,
      'rail': self.rail,
      'name': self.name,
      'vkCategory': self.vkCategory,
      'category': self.category,
      'description': self.description,
      'price': self.price.serialize(),
      'vkId': self.vkId,
      'timestamp': self.timestamp,
    }

  @staticmethod
  def deserialize(values: Dict[str, Any]):
    return Thing(
      article=values['article'],
      rail=values['rail'],
      name=values['name'],
      vkCategory=values.get('vkCategory'),
      category=values.get('category'),
      description=values['description'],
      price=Price.deserialize(values['price']),
      vkId=values['vkId'],
      timestamp=values.get('timestamp'),
    )

  def __init__(
    self,
    article: Optional[int] = None,
    rail: Optional[str] = None,
    name: Optional[str] = None,
    photoFilename: Optional[str] = None,
    vkCategory: Optional[int] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    price: Optional[Price] = None,
    vkId: Optional[int] = None,
    timestamp: Optional[dt.datetime] = None,
  ):
    Notifier.__init__(self)
    self.article = article
    self.rail = rail
    self.name = name
    self.photoFilename = photoFilename
    self.vkCategory = vkCategory
    self.category = category
    self.description = description
    self.price = price
    self.vkId = vkId
    self.timestamp = timestamp

  def __str__(self):
    return str(self.__dict__)


# END
