import datetime as dt
import traceback

from gspread.utils import ValueInputOption
from typing import Optional

from src.domain.locator import LocatorStorage
from src.domain.models.thing import Thing, Price
from src.utils.datetime.utils import cut_time


class SheetStats(LocatorStorage):

  def __init__(self, locator):
    super().__init__(locator)
    self.config = self.locator.config()
    self.spreadsheet = self.locator.spreadSheet()
    self.sheetStats = self.spreadsheet.worksheet(self.config.googleSheetStats())
    self.timestampFmt = self.config.googleTimestampFmt()
    self.dateFmt = self.config.googleDateFmt()
    self.categories = self.locator.config().categories()
    self.logger = self.locator.logger()

  def addRow(
    self,
    thing: Thing,
    price: int,
    countOnRail: int,
    countAll: int,
  ) -> bool:
    try:
      match thing.price.type:
        case Price.FIXED:
          fixedPrice = thing.price.fixedPrice
        case Price.DEFAULT_FIXED:
          fixedPrice = self.config.defaultFixedPrice()
        case Price.FREE:
          fixedPrice = 0
        case _:
          raise Exception('Price type error.')
      self.sheetStats.append_row(
        values=[
          dt.datetime.now().strftime(self.timestampFmt),  #Время продажи
          thing.article,  #Артикул
          thing.timestamp.strftime(self.timestampFmt)
          if thing.timestamp is not None else None,  #Время появления
          thing.rail,  #Номер рейла
          self.config.findCateogryByInternalId(
            thing.category).buttonTitle,  #Категория
          thing.price.type,  #Ценовая политика
          fixedPrice,  #Установленная цена
          price,  #Цена продажи
          countOnRail,  #Кол-во вещей на рейле
          countAll,  #Общее кол-во вещей
          thing.lifetime(),  #Время жизни,
        ],
        value_input_option=ValueInputOption.user_entered,
      )
      return True
    except Exception:
      self._error(traceback.format_exc())
      return False

  def _error(self, report):
    self.logger.error(report)