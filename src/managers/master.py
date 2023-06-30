import asyncio
import datetime as dt
from typing import Optional, List

from src.domain.locator import LocatorStorage, Locator
from src.domain.models.thing import Thing, Price
from src.managers.sheet.sheet import PaymentType
from src.utils.tg.piece import P
from src.utils.tg.send_message import send_message
from src.utils.datetime.utils import cut_time


class Master(LocatorStorage):

  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.repo = self.locator.repo()
    self.vk = self.locator.vk()
    self.sheet = self.locator.sheet()
    self.sheetStats = self.locator.sheetStats()
    self.config = self.locator.config()

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
      self.repo.removeThing(article)
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

  def sellThings(
    self,
    donate: int,
    paymentType: PaymentType,
    articles: List[int],
  ) -> [List[int, Optional[int]], List[int]]:
    self.addPurchase(price=donate, paymentType=paymentType)
    things = [self.getThing(a) for a in articles]
    averageExtraPrice = self._averageExtraPrice(things, donate)
    thingsFinalPrice = self._distributedDonate(averageExtraPrice, things)
    isNotSold = []
    isSold = []
    for article, price in thingsFinalPrice:
      thing = self.getThing(article)
      self._pushStats(
        price=price,
        thing=thing,
      )
      lifetime = (cut_time(dt.datetime.now()) -
                  cut_time(thing.timestamp)).days if thing.timestamp is not None else None
      if self.removeThing(article):
        isSold.append([article, lifetime])
      else:
        isNotSold.append(article)
    return [isSold, isNotSold]


  def getAllThings(self) -> List[Thing]:
    return self.repo.getAllThings()

  def getCountAllThings(self) -> int:
    return len(self.getAllThings())

  def getThingsOnRail(self, rail: str) -> List[Thing]:
    return self.repo.getThingsOnRail(rail)

  def getCountThingsOnRail(self, rail: str) -> int:
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

  def addPurchase(
    self,
    price: int,
    paymentType: PaymentType,
  ):
    return self.sheet.addPurchase(price, paymentType)

  def _pushStats(self, price: int, thing: Thing) -> bool:
    return self.sheetStats.addRow(
      thing=thing,
      price=price,
      countOnRail=self.getCountThingsOnRail(thing.rail),
      countAll=self.getCountAllThings(),
    )

  def _distributedDonate(self, averageExtraPrice,
                         things: List[Thing]) -> {int, int}:
    allFixed = len(
      [thing for thing in things if thing.price.type == Price.FREE]) == 0
    thingsFinalPrice = dict.fromkeys([thing.article for thing in things])
    for thing in things:
      match thing.price.type:
        case Price.FREE:
          thingsFinalPrice[thing.article] = averageExtraPrice
        case Price.DEFAULT_FIXED:
          thingsFinalPrice[thing.article] = self.config.defaultFixedPrice(
          ) + averageExtraPrice if allFixed else 0
        case Price.FIXED:
          thingsFinalPrice[
            thing.
            article] = thing.price.fixedPrice + averageExtraPrice if allFixed else 0
        case _:
          raise Exception('Price type error.')
    return things

  def _averageExtraPrice(self, things: List[Thing], donate: int):
    thingsFixedPrice = [
      thing.price.fixedPrice or self.config.defaultFixedPrice()
      for thing in things
      if thing.price.type != Price.FREE
    ]
    sumFixedPrice = sum(thingsFixedPrice)
    countFixedPrice = len(thingsFixedPrice)
    countFreePrice = len(
      [thing for thing in things if thing.price.type == Price.FREE])
    allFixed = (countFreePrice == 0)
    count = countFreePrice if not allFixed else countFixedPrice
    averageExtraPrice = ((donate - sumFixedPrice) /
                         count) if donate != sumFixedPrice else 0
    return averageExtraPrice

  async def sendDailyInfoToGroup(self):
    print(self.locator.config().tgGroupId())
    await send_message(
      tg=self.locator.tg(),
      chat=self.locator.config().tgGroupId(),
      text=self.locator.info().dailySummary(),
    )

# END
