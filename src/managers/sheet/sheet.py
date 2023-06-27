import datetime as dt

from gspread import service_account
from gspread.utils import ValueInputOption
from typing import Optional

from src.domain.locator import LocatorStorage


class PaymentType:
  TINK = 'Тинька Иры'
  SBER = 'Сбер Иры'
  CASH = 'Наличные'
  
  @staticmethod
  def getTypes():
    return [
      PaymentType.TINK,
      PaymentType.SBER,
      PaymentType.CASH,
    ]


class Sheet(LocatorStorage):
  def __init__(self, locator):
    super().__init__(locator)
    self.config = self.locator.config()
    self.account = service_account(filename=self.config.googleKeyFile())
    self.spreadsheet = self.account.open(self.config.googleSpreadsheet())
    self.sheet = self.spreadsheet.worksheet(self.config.googleSheet())
    self.timestampFmt = self.config.googleTimestampFmt()
    self.dateFmt = self.config.googleDateFmt()
    self.sumPlace = self.config.googleSumPlace()

  def addPurchase(self, price: int, paymentType: PaymentType):
    self.sheet.append_row(values=[dt.datetime.now().strftime(self.timestampFmt),
                                  price, paymentType],
                          value_input_option=ValueInputOption.user_entered)
    total = int(self.getMonthlyTotal())
    if total > self.config.rent() > total-price:
      self.locator.master().alertPayOff(total)


  def getMonthlyTotal(self) -> Optional[int]:
    monthes = self.sheet.get_values(self.sumPlace)
    monthes = list(map(lambda row: [row[0], dt.datetime.strptime(row[1], self.dateFmt)], monthes))
    for i in range(len(monthes) - 1):
      if monthes[i][1] <= dt.datetime.now() < monthes[i + 1][1]:
        return monthes[i][0]
    return monthes[-1][0] if len(monthes) > 0 else None
