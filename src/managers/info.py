import datetime as dt

from src.domain.locator import LocatorStorage, Locator
from src.utils.tg.piece import Pieces, P


class InfoManager(LocatorStorage):

  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.sheet = self.locator.sheet()
    self.repo = self.locator.repo()

  def dailySummary(self) -> Pieces:
    title = P('📈 ') + P(
      f'Горячая сводка от {self.today()}',
      types=['italic', 'bold', 'underline'],
    )

    first, last = self.sheet.getCurrentMonthEdges()
    month = P(f'Месяц: {self.month(first.month)} '
              f'({first.strftime("%d %B")} — {last.strftime("%d %B")})')

    money = P(f'Собрано: ') + P(
      f'{self.rubles(self.sheet.getMonthlyTotal())}',
      types='code',
    )

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
