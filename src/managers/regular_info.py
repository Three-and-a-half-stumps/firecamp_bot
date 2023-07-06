import asyncio
import datetime as dt

from src.domain.locator import LocatorStorage, Locator
from src.utils.datetime.utils import datetime_copy_with, is_today


class RegularInfo(LocatorStorage):
  LAST_DAY_INFORMED_LIRA_ID = 'RegularInfo_LAST_DAY_INFORMED'

  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.lira = self.locator.lira()
    self.config = self.locator.config()
    self.thread = None
    self.dailyInfoTime = self.config.dailyInfoTime()
    self.lastDayInformed = self.lira.get(
      RegularInfo.LAST_DAY_INFORMED_LIRA_ID,
      default=dt.datetime.today() - dt.timedelta(days=1),
    )

  async def start(self):
    while True:
      await asyncio.sleep(5)
      now = dt.datetime.now()
      dailyTime = datetime_copy_with(
        now,
        hour=self.dailyInfoTime.hours,
        minute=self.dailyInfoTime.minutes,
      )
      if now >= dailyTime and not is_today(self.lastDayInformed):
        await self._sendInfo()

  async def _sendInfo(self):
    try:
      await self.locator.master().sendDailyInfoToGroup()
      self.lastDayInformed = dt.datetime.today()
      self.lira.put(
        self.lastDayInformed,
        id=RegularInfo.LAST_DAY_INFORMED_LIRA_ID,
      )
      self.lira.flush()
    except Exception as e:
      self.locator.logger().error(f'RegularInfo::_sendInfo Exception: {e}')
