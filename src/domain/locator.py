import os
import sys

from src.domain.commands import global_command_list


class Locator:

  def __init__(self):
    self._commandsManager = None
    self._config = None
    self._inputFieldsConstructor = None
    self._lira = None
    self._logger = None
    self._loggerStream = None
    self._master = None
    self._repo = None
    self._sheet = None
    self._sheetStats = None
    self._sysLogger = None
    self._tg = None
    self._tgLog = None
    self._thingsRepo = None
    self._validatorsConstructor = None
    self._vk = None

  def commandsManager(self):
    if self._commandsManager is None:
      from src.managers.commands import CommandsManager
      self._commandsManager = CommandsManager(self, global_command_list)
    return self._commandsManager

  def config(self):
    if self._config is None:
      from src.domain.config import Config
      self._config = Config(filename=sys.argv[1] if len(sys.argv) > 1 else None)
    return self._config

  def inputFieldsConstructor(self):
    if self._inputFieldsConstructor is None:
      from src.managers.tg.input_fields import InputFieldsConstructor
      self._inputFieldsConstructor = InputFieldsConstructor(self)
    return self._inputFieldsConstructor

  def lira(self):
    if self._lira is None:
      from src.utils.lira import Lira
      datafile = self.config().liraDataFile()
      headfile = self.config().liraHeadFile()
      os.makedirs(os.path.dirname(datafile), exist_ok=True)
      os.makedirs(os.path.dirname(headfile), exist_ok=True)
      self._lira = Lira(datafile, headfile)
    return self._lira

  def logger(self):
    if self._logger is None:
      from src.utils.tg.tg_logger import TgLogger
      self._logger = TgLogger(
        self.sysLogger(),
        self.tgLog(),
        self.config().loggingDefaultChats(),
      )
    return self._logger

  def loggerStream(self):
    if self._loggerStream is None:
      from src.utils.tg.tg_logger_stream import TelegramLoggerStream
      self._loggerStream = TelegramLoggerStream(
        chats=self.config().loggingDefaultChats(),
        tg=self.tgLog(),
      )
    return self._loggerStream

  def sysLogger(self):
    if self._sysLogger is None:
      import logging
      logging.basicConfig(
        format=self.config().loggingFormat(),
        datefmt=self.config().loggingDateFormat(),
        stream=self.loggerStream(),
      )
      self._sysLogger = logging.getLogger('global')
      self._sysLogger.setLevel(logging.INFO)
      self._sysLogger.com = lambda com, m: self._sysLogger.info(
        f'{com} {m.chat.id}')
    return self._sysLogger

  def master(self):
    if self._master is None:
      from src.managers.master import Master
      self._master = Master(self)
    return self._master

  def repo(self):
    if self._repo is None:
      from src.managers.repo.repo import Repo
      self._repo = Repo(self)
    return self._repo

  def sheet(self):
    if self._sheet is None:
      from src.managers.sheet.sheet import Sheet
      self._sheet = Sheet(self)
    return self._sheet

  def sheetStats(self):
    if self._sheet_stats is None:
      from src.managers.sheet.sheetstats import SheetStats
      self._sheetStats = SheetStats(self)
    return self._sheet_stats

  def tg(self):
    if self._tg is None:
      from telebot.async_telebot import AsyncTeleBot
      self._tg = AsyncTeleBot(token=self.config().tgToken())
    return self._tg

  def tgLog(self):
    if self._tgLog is None:
      from telebot.async_telebot import AsyncTeleBot
      self._tgLog = AsyncTeleBot(token=self.config().tgLogToken())
    return self._tgLog

  def thingsRepo(self):
    if self._thingsRepo is None:
      from src.repositories.things_repo import ThingsRepo
      self._thingsRepo = ThingsRepo(self.lira())
    return self._thingsRepo

  def validatorsConstructor(self):
    if self._validatorsConstructor is None:
      from src.managers.tg.validators import ValidatorsConstructor
      self._validatorsConstructor = ValidatorsConstructor(self)
    return self._validatorsConstructor

  def vk(self):
    if self._vk is None:
      from src.managers.vk.vk import Vk
      self._vk = Vk(self)
    return self._vk


class LocatorStorage:

  def __init__(self, locator: Locator = None):
    self.locator = locator or Locator


_global_locator = Locator()


def glob():
  return _global_locator
