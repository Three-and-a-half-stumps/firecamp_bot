import asyncio
import inspect

from typing import Callable, Iterable, Any


class CallbackWrapper:
  def __init__(self, callback: Callable, **kwargs):
    self.kwargs = kwargs
    self.callback = callback
  
  def __call__(self, *args, **kwargs):
    for key, value in self.kwargs.items():
      kwargs[key] = value
    return self.callback(*args, **kwargs)


def reduce_list(fun: Callable, iterable: Iterable, start: Any):
  for value in iterable:
    start = fun(start, value)
  return start


def insert_between(values: [], term) -> []:
  if len(values) == 0:
    return values
  result = [values[0]]
  for value in values[1:]:
    result.extend([term, value])
  return result


async def maybeAwait(result):
  if inspect.isawaitable(result):
    return await result
  return result