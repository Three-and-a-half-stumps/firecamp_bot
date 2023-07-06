import asyncio
from sys import stdout
from typing import List

from telebot.async_telebot import AsyncTeleBot

from src.utils.tg.tg_destination import TgDestination


class TelegramLoggerStream:

  def __init__(self, tg: AsyncTeleBot, chats: List[TgDestination]):
    self.tg = tg
    self.chats = chats

  def write(self, report):
    stdout.write(report)
    if 'Too Many Requests: retry after' in report:
      return
    for chat in self.chats:
      asyncio.create_task(
        self.tg.send_message(
          chat_id=chat.chatId,
          reply_to_message_id=chat.messageToReplayId,
          text=report,
          disable_web_page_preview=True,
        ))
