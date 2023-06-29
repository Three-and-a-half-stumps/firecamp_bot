#!python3
import asyncio
import src.domain.models.thing as thing_module
import src.domain.thing as old_thing_module

from src.domain.locator import glob
from src.utils.tg.send_message import set_send_message_logger


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
  logger = locator.logger()
  set_send_message_logger(logger)
  commands = locator.commandsManager()
  await commands.addCommandsToMenu()
  commands.addHandlers()
  logger.info('Firecamp bot started')
  await locator.tg().infinity_polling()
  logger.info('Firecamp bot finished')


if __name__ == '__main__':
  asyncio.run(main())
