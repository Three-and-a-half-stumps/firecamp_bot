import traceback

from threading import Thread

from vk_api.bot_longpoll import VkBotLongPoll, VkBotEvent, VkBotEventType

from src.domain.locator import LocatorStorage, Locator


class VkGroupEventHandler(LocatorStorage):

  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.vk = self.locator.vkApi()
    self.asyncQueues = self.locator.asyncQueues()
    self.logger = self.locator.logger()
    self.groupId = -self.locator.config().vkGroupId()
    self.longpoll = VkBotLongPoll(self.vk, self.groupId)
    self.config = self.locator.config()
    self.thread = None

  def start(self):
    self.thread = Thread(target=self._target).start()

  def _target(self):
    self._info('vk longpoll: started')
    while True:
      try:
        for event in self.longpoll.listen():
          self._handleEvent(event)
      except Exception:
        self._error(traceback.format_exc())
        self._info('vk longpoll: reconnection')

  def _handleEvent(self, event: VkBotEvent):
    if event.type == VkBotEventType.MESSAGE_NEW:
      self._handleMessage(event.object.message)
    elif (event.type == VkBotEventType.WALL_POST_NEW and
          event.object['post_type'] == 'post'):
      try:
        if "copy_history" in event.object:
          self._handlePost(event.object.copy_history[0], event.object['text'])
        else:
          self._handlePost(event.object)
      except Exception:
        self._error(traceback.format_exc())

  def _handleMessage(self, message):
    self._info(f'(VK handle message) {message["text"]}')

  def _handlePost(self, object, text=None):
    self._info(f'(VK handle post) object: {object}, text: {text}')

  # ACCESSORY
  def _info(self, report):
    self._asyncAction(lambda: self.logger.info(report))

  def _error(self, report):
    self._asyncAction(lambda: self.logger.error(report))

  def _asyncAction(self, action):

    async def act():
      action()

    self.asyncQueues.putVk(act())
