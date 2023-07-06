import datetime as dt

from gspread import service_account
from gspread.utils import ValueInputOption
from typing import Optional

from src.domain.locator import LocatorStorage
from src.managers.sheet.sheet import PaymentType
from src.domain.models.thing import Thing, Price


class SheetStats(LocatorStorage):

  def __init__(self, locator):
    super().__init__(locator)
    self.config = self.locator.config()
    self.spreadsheet = self.locator.spreadSheet()
    self.sheet = self.spreadsheet.worksheet(self.config.googleSheetStats())
    self.timestampFmt = self.config.googleTimestampFmt()
    self.dateFmt = self.config.googleDateFmt()

  def addRow(
    self,
    thing: Thing,
    price: int,
    countOnRail: int,
    countAll: int,
  ) -> bool:
    try:
      lifetime = (dt.datetime.now() -
                  thing.timestamp) if thing.timestamp is not None else None
      match thing.price.type:
        case Price.FIXED:
          fixedPrice = thing.price.fixedPrice
        case Price.DEFAULT_FIXED:
          fixedPrice = self.config.defaultFixedPrice()
        case Price.FREE:
          fixedPrice = 0
        case _:
          raise Exception('Price type error.')
      self.sheet.append_row(
        values=[
          dt.datetime.now().strftime(self.timestampFmt),  #Время продажи
          thing.article,  #Артикул
          thing.timestamp.strftime(self.timestampFmt)
          if thing.timestamp is not None else None,  #Время появления
          thing.rail,  #Номер рейла
          thing.category,  #Категория
          thing.price.type,  #Ценовая политика
          fixedPrice,  #Установленная цена
          price,  #Цена продажи
          countOnRail,  #Кол-во вещей на рейле
          countAll,  #Общее кол-во вещей
          lifetime.days
          if isinstance(lifetime, dt.timedelta) else None,  #Время жизни,
        ],
        value_input_option=ValueInputOption.user_entered,
      )
      return True
    except Exception:
      return False
