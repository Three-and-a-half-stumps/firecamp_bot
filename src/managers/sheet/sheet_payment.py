import datetime as dt
import traceback

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


class SheetPayment(LocatorStorage):

  def __init__(self, locator):
    super().__init__(locator)
    self.config = self.locator.config()
    self.spreadsheet = self.locator.spreadSheet()
    self.sheetPayment = self.spreadsheet.worksheet(
      self.config.googleSheetPayment())
    self.timestampFmt = self.config.googleTimestampFmt()
    self.dateFmt = self.config.googleDateFmt()
    self.sumPlace = self.config.googleSumPlace()
    self.monthesPlace = self.config.googleMonthesPlace()
    self.logger = self.locator.logger()

  def addPurchase(self, price: int, paymentType: PaymentType) -> bool:
    try:
      self.sheetPayment.append_row(
        values=[
          dt.datetime.now().strftime(self.timestampFmt),
          price,
          paymentType,
        ],
        value_input_option=ValueInputOption.user_entered,
      )
      total = int(self.getMonthlyTotal())
      if total > self.config.rent() > total - price:
        self.locator.master().alertPayOff(total)
      return True
    except Exception:
      self._error(traceback.format_exc())
      return False

  def getMonthlyTotal(self) -> Optional[int]:
    monthes = self.sheetPayment.get_values(self.sumPlace)
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
    monthes = self.sheetPayment.get_values(self.monthesPlace)
    monthes = [dt.datetime.strptime(row[0], self.dateFmt) for row in monthes]
    for i in range(len(monthes) - 1):
      if monthes[i] <= dt.datetime.today() < monthes[i + 1]:
        return monthes[i], monthes[i + 1] - dt.timedelta(days=1)
    raise Exception(f'Today does not included in monthes: {monthes}')

  def _error(self, report):
    self.logger.error(report)