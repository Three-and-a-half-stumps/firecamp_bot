import asyncio
import sys
import traceback

from asyncio import Queue
from typing import Coroutine, Any, Callable


class FutureQueue:

  def __init__(self, workersCount: int = 1):
    self.queue = Queue()
    self.workersCount = workersCount
    self.workers = []
    self._printExceptionFunction = None

  def run(self):
    self.workers = [
      asyncio.create_task(self._run()) for _ in range(self.workersCount)
    ]

  async def _run(self):
    while True:
      task = await self.queue.get()
      try:
        if task is None:
          self.queue.task_done()
          break
        elif isinstance(task, _Future):
          task.result = await task.task
        else:
          await task
      except Exception as e:
        if isinstance(task, _Future):
          task.result = e
        else:
          self._printException(e)
      self.queue.task_done()

  async def join(self):
    [self.queue.put_nowait(None) for _ in range(self.workersCount)]
    await self.queue.join()

  def put(self, task):
    self.queue.put_nowait(task)

  def putFuture(self, task) -> Coroutine:
    future = _Future(task)
    self.queue.put_nowait(future)
    return future.get()

  def setPrintExceptionFunction(self, fun: Callable[[Exception], Any]):
    self._printExceptionFunction = fun

  def _printException(self, e: Exception):
    if self._printExceptionFunction is not None:
      self._printExceptionFunction(e)
    else:
      print(traceback.format_exc(), file=sys.stderr)


class _Future:

  def __init__(self, task):
    self.task = task
    self.result = None

  async def get(self):
    while True:
      if isinstance(self.result, Exception):
        raise self.result
      elif self.result is not None:
        return self.result
      await asyncio.sleep(0.01)
