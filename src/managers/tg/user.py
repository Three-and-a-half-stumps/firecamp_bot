import asyncio

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, Message

from src.domain.locator import LocatorStorage, Locator
from src.domain.models.thing import Thing, Price
from src.utils.tg.piece import P
from src.utils.tg.send_message import send_message
from src.utils.tg.tg_destination import TgDestination
from src.utils.tg.tg_input_form import TgInputForm
from src.utils.tg.tg_state import TgState


class User(TgState, LocatorStorage):

  def __init__(self, locator: Locator, chat: TgDestination):
    LocatorStorage.__init__(self, locator)
    TgState.__init__(self)
    self.chat = chat
    self.tg: AsyncTeleBot = self.locator.tg()
    self.master = self.locator.master()
    self.config = self.locator.config()
    self.logger = self.locator.logger()
    self.inputFields = self.locator.inputFieldsConstructor().chat(self.chat)
    self.info = self.locator.info()

  # OVERRIDES
  async def _onTerminate(self):
    pass

  async def _handleMessageBefore(self, m: Message) -> bool:
    return not self._checkTrusted()

  async def _handleMessage(self, m: Message) -> bool:
    self.send(
      P(
        'Не очень понятно, что ты хочешь.. используй команду',
        emoji='fail',
      ))
    return True

  async def _handleCallbackQuery(self, q: CallbackQuery) -> bool:
    asyncio.create_task(self.tg.answer_callback_query(q.id, 'Непонятно..'))
    return True

  # COMMAND HANDLERS
  async def handleStart(self):
    if not self._checkTrusted():
      return
    self.send('Привет, костровой!')

  async def handleNew(self):
    if not self._checkTrusted():
      return
    await self._handleNew()

  async def handleNewNew(self):
    if not self._checkDev():
      return
    await self._handleNew(setActionTimestamp=True)

  async def handleFind(self):
    if not self._checkTrusted():
      return

    async def articleEntered(article):
      thing = self.master.getThing(article)
      self.send(f'Рейл: {thing.rail}')
      await self.resetTgState()

    await self.setTgState(
      self.inputFields.existedThingArticle(onEntered=articleEntered))

  async def handleMove(self):
    if not self._checkTrusted():
      return

    async def form_entered(data):
      if self.master.changeThingRail(data[0], data[1], data[2]):
        self.send(P('Всё получилось!!', emoji='ok'))
      else:
        self.send(P('Такой вещи нет :(', emoji='fail'))
      await self.resetTgState()

    await self.setTgState(
      TgInputForm(
        tg=self.tg,
        chat=self.chat,
        on_form_entered=form_entered,
        terminate_message='Перемещение вещи прервано',
        fields=[
          self.inputFields.existedThingArticle(),
          self.inputFields.thingRailNum('Введите новый номер рейла'),
          self.inputFields.thingPricePolicy(),
        ],
      ))

  async def handleDelete(self):
    if not self._checkTrusted():
      return

    async def articleEntered(article):
      if self.master.removeThing(article):
        self.send(P('Вещь успешно удалена!', emoji='ok'))
      else:
        self.send(P('Такой вещи не припомню..', emoji='fail'))
      await self.resetTgState()

    await self.setTgState(
      self.inputFields.existedThingArticle(onEntered=articleEntered))

  async def handleSale(self):
    if not self._checkTrusted():
      return

    async def formEntered(data):
      isSold, isNotSold = self.master.sellThings(
        donate=data[1],
        paymentType=data[2],
        articles=data[0],
      )

      if len(isNotSold) == 0:
        self.send(
          P('Вещи успешно проданы!', emoji='ok') + '\n\n' +
          self.info.resultsOfLifetime(isSold))
      else:
        self.send(
          P(f'Вещи {", ".join(isSold)} успешно проданы!', emoji='ok') + '\n\n' +
          self.info.resultsOfLifetime(isSold))
        self.send(
          P(f'Вещи {", ".join(isNotSold)} продать не удалось. Обратитесь к фиксикам',
            emoji='fail'))
      await self.resetTgState()

    await self.setTgState(
      TgInputForm(
        tg=self.tg,
        chat=self.chat,
        on_form_entered=formEntered,
        terminate_message='Продажа вещи прервана',
        fields=[
          self.inputFields.existedThingArticleList(),
          self.inputFields.naturalInt('За сколько продали?'),
          self.inputFields.thingPaymentType(),
        ],
      ))

  async def handleSaleUntagged(self):
    if not self._checkTrusted():
      return

    async def formEntered(data):
      if self.master.addPurchase(price=data[0], paymentType=data[1]):
        self.send(P('Вещи успешно проданы!', emoji='ok'))
      else:
        self.send(P(f'Что-то пошло не так..', emoji='fail'))
      await self.resetTgState()

    self.send(P('ВНИМАНИЕ!!! Только для вещей без бирки', emoji='warning'))
    await self.setTgState(
      TgInputForm(
        tg=self.tg,
        chat=self.chat,
        on_form_entered=formEntered,
        terminate_message='Продажа вещи прервана',
        fields=[
          self.inputFields.naturalInt('За сколько продали?'),
          self.inputFields.thingPaymentType(),
        ],
      ))

  async def handleTotal(self):
    if not self._checkTrusted(checkGroup=True):
      return
    self.send(self.info.monthlyTotalMessage())

  async def handleDaily(self):
    if not self._checkTrusted(checkGroup=True):
      return
    self.send(self.info.dailySummary())

  async def handleReadd(self):
    if not self._checkDev():
      return

    async def formEntered(data):
      if self.master.reAddThing(
          article=data[0],
          newName=data[1],
          newDescription=data[2],
      ):
        self.send(P('Продукт успешно пересоздан.', emoji='ok'))
      else:
        self.send(P('Что-то пошло не так..', emoji='fail'))
      await self.resetTgState()

    await self.setTgState(
      TgInputForm(
        tg=self.tg,
        chat=self.chat,
        on_form_entered=formEntered,
        terminate_message='Перезалив товара прерван',
        fields=[
          self.inputFields.existedThingArticle(),
          self.inputFields.thingName('Введите новое название вещи'),
          self.inputFields.thingDescription('Введите новое описание вещи'),
        ],
      ))

  async def handleCountThings(self):
    if not self._checkTrusted():
      return
    self.send(f'Вещей - {self.master.getCountAllThings()} шт.')

  async def handleCountThingsOnRail(self):
    if not self._checkTrusted():
      return

    async def railEntered(rail):
      countOnRail = self.master.getCountThingsOnRail(rail)
      if countOnRail != 0:
        self.send(f'Вещей на {rail} рейле - {countOnRail} шт.')
      else:
        self.send(P(f'На рейле {rail} нет ни одной вещи.', emoji='fail'))
      await self.resetTgState()

    await self.setTgState(self.inputFields.thingRailNum(onEntered=railEntered))

  # ACCESSORY
  def send(self, text):
    asyncio.create_task(send_message(tg=self.tg, chat=self.chat, text=text))

  # OTHER
  async def _handleNew(self, setActionTimestamp: bool = False):

    async def formEntered(data):
      print(f'photo: {data[0]}')
      article = self.master.newThing(
        Thing(
          rail=data[2],
          name=data[1],
          photoFilename=data[0],
          vkCategory=5001,
          category=data[4],
          description=data[5],
          price=data[3],
          timestamp=data[6] if setActionTimestamp else None,
        ))
      if article is not None:
        self.send(P('Вещь успешно добавлена. Артикул: %i' % article,
                    emoji='ok'))
      else:
        self.send(P(
          'Что-то пошло не так.. попробуйте ещё раз',
          emoji='fail',
        ))
      await self.resetTgState()

    await self.setTgState(
      TgInputForm(
        tg=self.tg,
        chat=self.chat,
        on_form_entered=formEntered,
        terminate_message='Добавление вещи прервано',
        fields=[
          self.inputFields.thingPhoto(),
          self.inputFields.thingName(),
          self.inputFields.thingRailNum(),
          self.inputFields.thingPricePolicy(),
          self.inputFields.thingCateogry(),
          self.inputFields.thingDescription(),
          *([self.inputFields.thingDatatime()] if setActionTimestamp else []),
        ],
      ))

  # CHECKS
  def _checkTrusted(self, checkGroup=False):
    if (self.chat.chatId in self.config.trustedUsers() or
        checkGroup and self.chat.chatId == self.config.tgGroupId()):
      return True
    self.send('Я вас не звал, идите наЬ#Я')
    return False

  def _checkDev(self):
    if self.chat.chatId in self.config.devUsers():
      return True
    self.send('Эта команда доступна только разработчикам.')
    return False
