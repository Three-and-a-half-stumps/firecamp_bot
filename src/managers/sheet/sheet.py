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
    self.monthesPlace = self.config.googleMonthesPlace()

  def addPurchase(self, price: int, paymentType: PaymentType):
    self.sheet.append_row(
      values=[
        dt.datetime.now().strftime(self.timestampFmt), price, paymentType
      ],
      value_input_option=ValueInputOption.user_entered,
    )
    total = int(self.getMonthlyTotal())
    if total > self.config.rent() > total - price:
      self.locator.master().alertPayOff(total)

  def getMonthlyTotal(self) -> Optional[int]:
    monthes = self.sheet.get_values(self.sumPlace)
    monthes = [
      [row[0], dt.datetime.strptime(row[1], self.dateFmt)] for row in monthes
    ]
    for i in range(len(monthes) - 1):
      if monthes[i][1] <= dt.datetime.now() < monthes[i + 1][1]:
        return int(monthes[i][0])
    return int(monthes[-1][0]) if len(monthes) > 0 else None

  def getCurrentMonthEdges(self) -> (dt.datetime, dt.datetime):
    """
    Возвращает первый и последний (включительно) день текущего месяца
    """
    monthes = self.sheet.get_values(self.monthesPlace)
    monthes = [dt.datetime.strptime(row[0], self.dateFmt) for row in monthes]
    for i in range(len(monthes) - 1):
      if monthes[i] <= dt.datetime.today() < monthes[i + 1]:
        return monthes[i], monthes[i + 1] - dt.timedelta(days=1)
    raise Exception(f'Today does not included in monthes: {monthes}')
