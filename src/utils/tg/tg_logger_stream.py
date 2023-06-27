import asyncio
from sys import stdout
from typing import List

from telebot.async_telebot import AsyncTeleBot


class TelegramLoggerStream:
  def __init__(self, tg: AsyncTeleBot, chats: List[int]):
    self.tg = tg
    self.chats = chats

  def write(self, report):
    for chat in self.chats:
      asyncio.create_task(
        self.tg.send_message(chat, report, disable_web_page_preview=True)
      )
    stdout.write(report)
