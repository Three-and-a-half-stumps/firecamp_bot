import asyncio
from logging import Logger

from telebot.async_telebot import AsyncTeleBot

from src.utils.tg.piece import Pieces
from src.utils.tg.tg_destination import TgDestination


class TgLogger:
  def __init__(self, logger: Logger, tg: AsyncTeleBot, chats: [TgDestination]):
    self.logger = logger
    self.tg = tg
    self.chats = chats

  def info(self, report, *args, **kwargs):
    self.logger.info(report, *args, **kwargs)

  def warning(self, report, *args, **kwargs):
    self.logger.warning(report, *args, **kwargs)

  def error(self, report, *args, **kwargs):
    self.logger.error(report, *args, **kwargs)

  def text(self, m, *args, **kwargs):
    self.info(f'[@{self._usernameIdOrId(m)}] {m.text}', *args, **kwargs)

  def answer(self, chat_id: int, text: str, *args, **kwargs):
    self.info(f'[{chat_id}]\n{text}', *args, **kwargs)

  def message(
    self,
    pieces: Pieces,
    chat_id = None,
    **kwargs,
  ):
    text, entities = pieces.toMessage()
    for chat in self.chats:
      if chat.chatId == chat_id:
        continue
      asyncio.create_task(self.tg.send_message(
        chat_id=chat.chatId,
        reply_to_message_id=chat.messageToReplayId,
        text=text,
        entities=entities,
        **kwargs))

  @staticmethod
  def _usernameIdOrId(m):
    return (f'{m.chat.username}|{m.chat.id}'
            if m.chat.username is not None
            else m.chat.id)
