#!python3
import asyncio

from src.domain.locator import glob
from src.utils.tg.send_message import set_send_message_logger


async def main():
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


# end