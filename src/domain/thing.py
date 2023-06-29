from typing import Optional


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


class Price:
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


class Thing:

  def __init__(
    self,
    article: Optional[int] = None,
    rail: Optional[str] = None,
    name: Optional[str] = None,
    photoFilename: Optional[str] = None,
    vkCategory: Optional[int] = None,
    category: Optional[Category] = None,
    description: Optional[str] = None,
    price: Optional[Price] = None,
    vkId: Optional[int] = None,
  ):
    self.article = article
    self.rail = rail
    self.name = name
    self.photoFilename = photoFilename
    self.vkCategory = vkCategory
    self.category = category
    self.description = description
    self.price = price
    self.vkId = vkId

  def __str__(self):
    return str(self.__dict__)


# END
