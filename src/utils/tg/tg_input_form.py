import asyncio
from copy import copy
from typing import List, Callable

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, Message

from ..utils import CallbackWrapper, maybeAwait
from .send_message import send_message
from .tg_input_field import TgInputField
from .tg_state import TgState


class TgInputForm(TgState):
  """
  Формочка, в которой последовательно вводятся некоторые данные
  """
  def __init__(
    self,
    tg: AsyncTeleBot,
    chat,
    on_form_entered: Callable,
    fields: List[TgInputField],
    terminate_message: str = None,
  ):
    """
    :param tg: Телебот, для общения с пользователем (отправка и редактировать сообщений)
    :param chat: чат, где происходит общение
    :param on_form_entered: коллбэк, вызывающийся, когда все поля формы заполнены
    :param fields: поля, которые нужно заполнить
    :param terminate_message: сообщение, выводящееся, если ввод формы прерван
    """
    super().__init__(on_enter_state=self._onEnterState)
    assert(len(fields) != 0)
    self.tg = tg
    self.chat = chat
    self.fields = fields
    self.onFormEntered = on_form_entered
    self.terminate_message = terminate_message
    self.data = [None] * len(self.fields)
    callbacks = [copy(field.onFieldEntered) for field in self.fields]
    for i in range(len(self.fields)):
      async def on_field_entered(data, num):
        callbacks[num](data)
        await self._onFieldDataEntered(data)
      self.fields[i].onFieldEntered = CallbackWrapper(on_field_entered, num=copy(i))

  
  # OVERRIDE METHODS
  async def _onTerminate(self):
    if self.terminate_message is not None:
      asyncio.create_task(send_message(
        tg=self.tg,
        chat=self.chat,
        text=self.terminate_message
      ))

  async def _handleMessage(self, m: Message) -> bool:
    raise Exception('Сообщение всегда должно обрабатываться в TgInputField')

  async def _handleCallbackQuery(self, q: CallbackQuery) -> bool:
    return False
  
  # MAIN METHODS
  async def _onEnterState(self):
    await self.setTgState(self.fields[0])
    
  async def _onFieldDataEntered(self, data):
    index = self.fields.index(self._substate)
    self.data[index] = data
    if index + 1 < len(self.fields):
      await self.setTgState(self.fields[index+1])
    else:
      await maybeAwait(self.onFormEntered(self.data))

  async def _handleMessageBefore(self, m: Message) -> bool:
    pass
