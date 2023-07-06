#!python3
import asyncio
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


async def main():
  migrateThing()
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
  regularInfo = locator.regularInfo()
  asyncio.create_task(regularInfo.start())

  # run
  logger.info('Firecamp bot started')
  await locator.tg().infinity_polling()
  logger.info('Firecamp bot finished')


if __name__ == '__main__':
  asyncio.run(main())
