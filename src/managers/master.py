import asyncio
from typing import Optional, List

from src.domain.locator import LocatorStorage, Locator
from src.domain.models.thing import Thing, Price
from src.managers.sheet.sheet import PaymentType
from src.utils.tg.piece import P
from src.utils.tg.send_message import send_message


class Master(LocatorStorage):

  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.repo = self.locator.repo()
    self.vk = self.locator.vk()
    self.sheet = self.locator.sheet()

  def newThing(self, thing: Thing) -> Optional[int]:
    thing.article = self.repo.makeNextArticle()
    thing.vkId = self.vk.addProduct(thing)
    if thing.vkId is None:
      self.repo.ungetLastArticle()
      thing.article = None
      return None
    self.repo.addThing(thing)
    return thing.article

  def reAddThing(
    self,
    article: int,
    newName: str,
    newDescription: str,
  ) -> bool:
    thing = self.repo.getThing(article)
    if thing is None:
      return False
    thing.name = newName
    thing.description = newDescription
    self.vk.removeProduct(thing.vkId)
    newVkId = self.vk.addProduct(thing)
    if newVkId is None:
      return False
    thing.vkId = newVkId
    thing.notify()
    return True

  def changeThingRail(
    self,
    article: int,
    newRail: str,
    price: Price = None,
  ) -> bool:
    thing = self.repo.getThing(article)
    if thing is None:
      return False
    thing.rail = newRail
    if price is not None and not (thing.price == price):
      thing.price = price
      self.vk.updateProduct(thing)
    thing.notify()
    return True

  def getThing(self, article: int) -> Optional[Thing]:
    return self.repo.getThing(article)

  def getMonthlyTotal(self) -> Optional[int]:
    return self.sheet.getMonthlyTotal()

  def getMonthEnd(self):
    return self.sheet.getMonthEnd()

  def removeThing(self, article: int) -> bool:
    thing = self.repo.getThing(article)
    if thing is None:
      return False
    self.vk.removeProduct(thing.vkId)
    self.repo.removeThing(article)
    return True

  def sellThing(
    self,
    price: int,
    paymentType: PaymentType,
    article: int = None,
  ) -> bool:
    if article is None or self.removeThing(article):
      self.sheet.addPurchase(price, paymentType)
      return True
    return False

  def getAllThings(self) -> List[Thing]:
    return self.repo.getAllThings()

  def getCountAllThings(self) -> int:
    return len(self.getAllThings())

  def getThingsOnRail(self, rail: int) -> List[Thing]:
    return self.repo.getThingsOnRail(rail)

  def getCountThingsOnRail(self, rail: int) -> int:
    return len(self.getThingsOnRail(rail))

  def alertPayOff(self, value: int):
    asyncio.create_task(
      send_message(
        tg=self.locator.tg(),
        chat=self.locator.config().tgGroupId(),
        text=P(
          f"Ура! Мы теперь работаем не платно. Накопили уже {value}",
          emoji='infoglob',
        ),
      ))


# END
