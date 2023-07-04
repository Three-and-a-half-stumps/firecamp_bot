import datetime as dt

from gspread import service_account
from gspread.utils import ValueInputOption
from typing import Optional

from src.domain.locator import LocatorStorage
from src.managers.sheet.sheet import PaymentType
from src.domain.models.thing import Thing


class Sheet_Stats(LocatorStorage):

  def __init__(self, locator):
    super().__init__(locator)
    self.config = self.locator.config()
    self.account = service_account(filename=self.config.googleKeyFile())
    self.spreadsheet = self.account.open(self.config.googleSpreadsheet())
    self.sheet = self.spreadsheet.worksheet(self.config.googleSheetStats())
    self.timestampFmt = self.config.googleTimestampFmt()
    self.dateFmt = self.config.googleDateFmt()
    self.lifetimePlace = self.config.googleLifetimePlace()

  def addRow(self, thing: Thing, price: int, countOnRail: int,
             countAll: int) -> int:
    self.sheet.append_row(
      values=[
        dt.datetime.now().strftime(self.timestampFmt),  #Время продажи
        thing.article,  #Артикул
        thing.timestamp,  #Время появления
        thing.rail,  #Номер рейла
        thing.category,  #Категория
        thing.price.type,  #Ценовая политика
        thing.price.fixedPrice,  #Установленная цена
        price,  #Цена продажи
        countOnRail,  #Кол-во вещей на рейле
        countAll,  #Общее кол-во вещей
      ],
      value_input_option=ValueInputOption.user_entered,
    )
    lifetimes = self.sheet.get_values(self.lifetimePlace)
    print(lifetimes[-1])
    return lifetimes[-1]
