#!python3
import asyncio
import datetime as dt
from random import randint

from typing import List

import src.domain.models.thing as thing_module
import src.domain.thing as old_thing_module
import locale

from src.domain.config import Config
from src.domain.locator import glob
from src.utils.tg.send_message import set_send_message_logger


def printThing(article: int):
  repo = glob().thingsRepo()
  print(repo.find(article))


def set_locale(config: Config):
  locale.setlocale(
    category=locale.LC_ALL,
    locale=config.locale(),
  )


def migrateThing():
  cat = old_thing_module.THING_CATEGORY
  lira = glob().lira()
  things = []
  for id in lira[cat]:
    oldThing = lira(id)
    things.append(
      thing_module.Thing(
        article=oldThing.article,
        rail=oldThing.rail,
        name=oldThing.name,
        vkCategory=oldThing.vkCategory,
        category=oldThing.category,
        description=oldThing.description,
        photoFilename=oldThing.photoFilename,
        price=thing_module.Price(
          oldThing.price.type,
          oldThing.price.fixedPrice,
        ),
        vkId=oldThing.vkId,
      ))

  [lira.out(id) for id in lira[cat]]
  repo = glob().thingsRepo()
  [repo.put(thing) for thing in things]


def migrateCategory():
  repo = glob().thingsRepo()
  things: List[thing_module.Thing] = repo.findAll(lambda _: True)
  for thing in things:
    if not isinstance(thing.category, int):
      thing.category = thing_module.Category.internalId(thing.category)
      thing.notify()


def setTimestampForOldThings():
  repo = glob().thingsRepo()
  things: List[thing_module.Thing] = repo.findAll(lambda _: True)
  first = dt.datetime(year=2023, month=5, day=1)
  last = dt.datetime(year=2023, month=6, day=1)
  daysDispersion = (last - first).days
  for thing in things:
    if thing.timestamp is None:
      thing.timestamp = first + dt.timedelta(days=randint(
        0,
        daysDispersion - 1,
      ))
      thing.notify()


async def main():
  migrateThing()
  migrateCategory()
  setTimestampForOldThings()
  locator = glob()
  set_locale(config=locator.config())

  # logger
  logger = locator.logger()
  set_send_message_logger(logger)

  # async queues
  asyncQueues = locator.asyncQueues()
  asyncQueues.run()

  # commands
  commands = locator.commandsManager()
  await commands.addCommandsToMenu()
  commands.addHandlers()

  # vk
  vk = locator.vkGroupEventHandler()
  vk.start()

  # regular info
  #regularInfo = locator.regularInfo()
  #asyncio.create_task(regularInfo.start())

  # run
  logger.info('Firecamp bot started')
  await locator.tg().infinity_polling()
  logger.info('Firecamp bot finished')


if __name__ == '__main__':
  asyncio.run(main())
