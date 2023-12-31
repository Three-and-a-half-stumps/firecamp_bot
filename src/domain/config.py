import json
from typing import List

from src.domain.models.category import Category
from src.domain.models.daily_info_time import DailyInfoTime
from src.utils.tg.tg_destination import TgDestination


class Config:
  DEFAULT_CONFIG_FILE_NAME = 'config.json'

  def __init__(self, filename: str = None):
    self.data = dict()
    if filename is None:
      filename = Config.DEFAULT_CONFIG_FILE_NAME
    with open(filename) as file:
      self.data = json.load(file)

  def loggingDefaultChats(self) -> [TgDestination]:
    return [
      TgDestination(
        chat_id=d['chat_id'],
        message_to_replay_id=d.get('message_to_replay_id'),
      ) for d in self._paramOrNone('logging_default_chats', list)
    ]

  def loggingDateFormat(self) -> str:
    return self._paramOrNone('logging_date_format', str)

  def loggingFormat(self) -> str:
    return self._paramOrNone('logging_format', str)

  def locale(self) -> str:
    return self._paramOrNone('locale', str)

  def photoDir(self) -> str:
    return self._paramOrNone('photo_dir', str)

  def tgToken(self) -> str:
    return self._paramOrNone('tg_token', str)

  def tgLogToken(self) -> str:
    return self._paramOrNone('tg_log_token', str)

  def tgGroupId(self) -> int:
    return self._paramOrNone('tg_group_id', int)

  def vkAccessToken(self) -> str:
    return self._paramOrNone('vk_access_token', str)

  def vkGroupId(self) -> int:
    return self._paramOrNone('vk_group_id', int)

  def googleKeyFile(self) -> str:
    return self._paramOrNone('google_key_file', str)

  def googleSpreadsheet(self) -> str:
    return self._paramOrNone('google_spreadsheet', str)

  def googleSheet(self) -> str:
    return self._paramOrNone('google_sheet', str)

  def googleTimestampFmt(self) -> str:
    return self._paramOrNone('google_timestamp_fmt', str)

  def googleDateFmt(self) -> str:
    return self._paramOrNone('google_date_fmt', str)

  def googleSumPlace(self) -> str:
    return self._paramOrNone('google_sum_place', str)

  def googleMonthesPlace(self) -> str:
    return self._paramOrNone('google_monthes_place', str)

  def defaultFixedPrice(self) -> int:
    return self._paramOrNone('default_fixed_price', int)

  def defaultFreePrice(self) -> int:
    return self._paramOrNone('default_free_price', int)

  def rent(self) -> int:
    return self._paramOrNone('rent', int)

  def liraHeadFile(self) -> str:
    return self._paramOrNone('lira_head_file', str)

  def liraDataFile(self) -> str:
    return self._paramOrNone('lira_data_file', str)

  def trustedUsers(self) -> List[int]:
    return self._paramOrNone('trusted_users', list)

  def devUsers(self) -> List[int]:
    return self._paramOrNone('dev_users', list)

  def categories(self) -> List[Category]:
    return [
      Category.fromJson(data) for data in self._paramOrNone('categories', list)
    ]

  def dailyInfoTime(self) -> DailyInfoTime:
    return DailyInfoTime.deserialize(self._paramOrNone('daily_info_time', dict))

  def findCateogryByInternalId(self, id: int) -> Category:
    return [cat for cat in self.categories() if cat.internalId == id][0]

  def _paramOrNone(self, name: str, tp):
    return Config._valueOrNone(self.data.get(name), tp)

  @staticmethod
  def _valueOrNone(value, tp):
    return value if type(value) is tp else None
