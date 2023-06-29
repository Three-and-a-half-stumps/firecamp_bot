import asyncio
from typing import List, Optional

from telebot.types import BotCommand, Message, CallbackQuery

from src.domain.commands import Command
from src.domain.locator import LocatorStorage
from src.managers.tg.user import User
from src.utils.tg.tg_destination import TgDestination


class CommandsManager(LocatorStorage):

  def __init__(self, locator, commands: List[Command]):
    super().__init__(locator)
    self.commands = commands
    self.tg = self.locator.tg()
    self.logger = self.locator.logger()
    self.config = self.locator.config()
    self.users = dict()

  async def addCommandsToMenu(self):
    await self.tg.set_my_commands([
      BotCommand(com.preview, com.description)
      for com in self.commands
      if com.addToMenu
    ])

  # decorators
  def logCommandDecorator(self, func):

    async def wrapper(m, res=False):
      self.logger.text(m)
      func(m, res)

    return wrapper

  def logMessageDecorator(self, func):

    async def wrapper(m: Message, res=False):
      if m.chat.id > 0:
        self.logger.text(m)
      func(m, res)

    return wrapper

  def findUserDecorator(self, func):

    def wrapper(m: Message, res=False):
      user = self._findUser(m.chat.id)
      func(user, m, res)

    return wrapper

  # handlers
  def addHandlers(self):
    self.addCommandHandlers()
    self.addMessageHandlers()
    self.addCallbackQueryHandlers()

  def addCommandHandlers(self):
    for command in self.commands:
      exec(f'''
@self.tg.message_handler(commands=[command.name])
@self.logCommandDecorator
@self.findUserDecorator
def handle_{command.name}(user, m, __):
  if user is not None:
    exec(f'asyncio.create_task(user.{command.handler}())')
      ''')

  def addMessageHandlers(self):

    @self.tg.message_handler(content_types=['text', 'photo', 'video'])
    @self.logMessageDecorator
    def handle_message(m: Message, __=False):
      user = self._findUser(m.chat.id)
      if user is not None:
        asyncio.create_task(user.handleMessage(m))

  def addCallbackQueryHandlers(self):

    @self.tg.callback_query_handler(func=lambda call: True)
    async def handle_callback_query(q: CallbackQuery):
      user = self._findUser(q.from_user.id)
      if user is not None:
        asyncio.create_task(user.handleCallbackQuery(q))

  def _findUser(self, chatId) -> Optional[User]:
    return self.users.setdefault(
      chatId, User(self.locator, TgDestination(chat_id=chatId)))
