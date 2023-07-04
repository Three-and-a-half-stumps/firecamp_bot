import traceback
from typing import Coroutine

from src.domain.locator import LocatorStorage, Locator
from src.utils.asyncio.future_queue import FutureQueue


class AsyncQueues(LocatorStorage):

  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.logger = self.locator.logger()
    self.vkQueue = FutureQueue()
    self.vkQueue.setPrintExceptionFunction(self._printException)

  def run(self):
    self.vkQueue.run()

  def putVk(self, task):
    self.vkQueue.put(task)

  def putVkFuture(self, task) -> Coroutine:
    return self.vkQueue.putFuture(task)

  def _printException(self, _: Exception):
    self.logger.error(traceback.format_exc())
