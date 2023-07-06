import datetime as dt
from typing import Optional

from src.domain.locator import LocatorStorage, Locator
from src.utils.tg.piece import Pieces, P


class InfoManager(LocatorStorage):
  """
  Собирает информация по всей программе
  """

  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.sheet = self.locator.sheet()
    self.repo = self.locator.repo()
    self.config = self.locator.config()

  def monthlyTotal(self) -> Optional[int]:
    return self.sheet.getMonthlyTotal()

  def currentMonthEdges(self) -> (dt.datetime, dt.datetime):
    return self.sheet.getCurrentMonthEdges()

  def monthlyTotalMessage(self) -> str:
    total = self.monthlyTotal()
    _, last = self.sheet.getCurrentMonthEdges()
    today = dt.datetime.today()
    today = dt.datetime(year=today.year, month=today.month, day=today.day)
    diff = (last - today).days + 1
    return (f'Собрано {self.rubles(total)} '
            f'А это аж {self.percent(total, self.config.rent())} от аренды. '
            f'До конца арендного месяца осталось {diff}д.')

  def dailySummary(self) -> Pieces:
    title = P(
      f'Горячая сводка от {self.today()}',
      types=['italic', 'bold', 'underline'],
      emoji='info_board',
    )

    first, last = self.sheet.getCurrentMonthEdges()
    month = P(f'Месяц: {self.month(first.month)} '
              f'({first.strftime("%d %B")} — {last.strftime("%d %B")})')

    total = self.sheet.getMonthlyTotal()
    money = P(f'Собрано: ') + P(
      f'{self.rubles(total)}',
      types='code',
    ) + P(f' ({self.percent(total, self.config.rent())})')

    things = P('Вещей в базе: ') + P(
      f'{self.locator.master().getCountAllThings()}',
      types='code',
    )
    return title + '\n\n' + month + '\n' + money + '\n' + things

  @staticmethod
  def today() -> str:
    return dt.datetime.today().strftime('%d %B, %A')

  @staticmethod
  def rubles(value: int) -> str:
    return f'{value}р.'

  @staticmethod
  def percent(value: int, hundred: int) -> str:
    percent = round(value / hundred * 100)
    return f'{percent}%'

  @staticmethod
  def month(value: int) -> str:
    return [
      'январь',
      'февраль',
      'март',
      'апрель',
      'май',
      'июнь',
      'июль',
      'август',
      'сентябрь',
      'октябрь',
      'ноябрь',
      'декабрь',
    ][value - 1]


# 🙁🫤😐🫡😏😀😆🥳😘🥰😍🤩😎
# ⛄️🌬🌱🌷💐🌻☀️🌞🔔🍁☔️❄️