from abc import abstractmethod
from typing import Callable

from telebot.types import CallbackQuery, Message

from src.utils.utils import maybeAwait


class TgState:
  """
  Представляет собой состояние, в котором находится телеграм бот. Позволяет:
  - установить события на вход и выход из состояния;
  - установить обработчики сообщений и запросов (перегрузите соответствующие функции)
  - устанавливать подсостояния, которым будет делегировать обработка сообщений и запросов
  """

  def __init__(
    self,
    on_enter_state: Callable = None,
  ):
    """
    :param on_enter_state: коллбэк, который вызывается при вхождении в состояние
    """
    self._onEnterState = on_enter_state
    self._substate = None

  async def start(self) -> None:
    """
    Должно быть вызвано при вхождении в состояние
    """
    if self._onEnterState is not None:
      await maybeAwait(self._onEnterState())

  async def terminate(self):
    """
    Должно быть вызвано после выхода из состояния
    """
    await self._onTerminate()

  async def terminateSubstate(self):
    """
    Вызывается, когда завершается подстотояние
    """
    if self._substate is not None:
      await self._substate.terminate()
      await self.resetTgState()

  async def setTgState(self, state, silent=False, terminate=True):
    """
    Установка подсостояния
    
    :param state: подстотояние
    :param silent: вызывать ли метод start у состояния (по умолчанию вызывает)
    :param terminate: завершить ли предыдущее подсостояние (по умолчанию завершает)
    """
    if terminate:
      await self.terminateSubstate()
    self._substate = state
    if not silent:
      await state.start()

  async def resetTgState(self):
    """
    Очищает подсостояние
    """
    self._substate = None

  async def handleMessage(self, m: Message) -> bool:
    """
    Обрабатывает сообщение (можно перегрузить метод _handleMessageBefore в дочернем классе,
    чтобы перехватить обработку; если этот метод возвратет True, то на этом обработка сообщения
    завершится). Если есть подсостояние, то в первую очередь происходит попытка обработать
    сообщение с помощью подсостояния.
    
    :param m: сообщение, которое нужно обработать
    :return: было ли обработано состояние
    """
    if (await self._handleMessageBefore(m) or
        (self._substate is not None and await self._substate.handleMessage(m))):
      return True
    return await self._handleMessage(m)

  async def handleCallbackQuery(self, q: CallbackQuery) -> bool:
    """
    Обрабатывает CallbackQuery (если есть подсостояние, то сначала пытаемся обработать подсостоянием)
    
    :param q: запрос, который нужно обработать
    :return: был ли обработан запрос
    """
    if self._substate is not None and await self._substate.handleCallbackQuery(q
                                                                              ):
      return True
    return await self._handleCallbackQuery(q)

  @abstractmethod
  async def _onTerminate(self):
    """
    Вызывается при завершении состояния
    """
    pass

  @abstractmethod
  async def _handleMessageBefore(self, m: Message) -> bool:
    """
    Обработка сообщения перед обработкой подсостоянием
    
    :param m: сообщение, которое нужно обработать
    :return: было ли обработано сообщение (следует ли остановить обработку?)
    """
    pass

  @abstractmethod
  async def _handleMessage(self, m: Message) -> bool:
    """
    Обработка сообщения (уже после подсостояния)
    
    :param m: сообщение, которое нужно обработать
    :return: было ли обработано сообщение
    """
    pass

  @abstractmethod
  async def _handleCallbackQuery(self, q: CallbackQuery) -> bool:
    """
    Обработа запроса callbackQuery
    
    :param q: запрос, который нужно обработать
    :return: был ли обработан запрос
    """
    pass
