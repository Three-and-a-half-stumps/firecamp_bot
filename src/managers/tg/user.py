import asyncio
import os
import re
import uuid
import datetime

from telebot.async_telebot import AsyncTeleBot
from telebot.types import CallbackQuery, Message

from src.domain.locator import LocatorStorage, Locator
from src.domain.thing import Category, Thing, Price
from src.managers.sheet.sheet import PaymentType
from src.utils.tg.piece import P
from src.utils.tg.send_message import send_message
from src.utils.tg.tg_destination import TgDestination
from src.utils.tg.tg_input_field import TgInputField, InputFieldButton
from src.utils.tg.tg_input_form import TgInputForm
from src.utils.tg.tg_state import TgState
from src.utils.tg.utils import list_to_layout
from src.utils.tg.value_validators import FunctionValidator, ValidatorObject, ChainValidator


class User(TgState, LocatorStorage):

  def __init__(self, locator: Locator, chat: TgDestination):
    LocatorStorage.__init__(self, locator)
    TgState.__init__(self)
    self.chat = chat
    self.tg: AsyncTeleBot = self.locator.tg()
    self.master = self.locator.master()
    self.config = self.locator.config()
    self.logger = self.locator.logger()

  # OVERRIDES
  async def _onTerminate(self):
    pass

  async def _handleMessageBefore(self, m: Message) -> bool:
    return not self._checkTrusted()

  async def _handleMessage(self, m: Message) -> bool:
    self.send(
      P('Не очень понятно, что ты хочешь.. используй команду', emoji='fail'))
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

    async def formEntered(data):
      article = self.master.newThing(
        Thing(
          rail=data[2],
          name=data[1],
          photoFilename=data[0],
          vkCategory=5001,
          category=data[4],
          description=data[5],
          price=data[3],
        ))
      self.send(P('Вещь успешно добавлена. Артикул: %i' % article, emoji='ok'))
      await self.resetTgState()

    await self.setTgState(
      TgInputForm(
        tg=self.tg,
        chat=self.chat,
        on_form_entered=formEntered,
        terminate_message='Добавление вещи прервано',
        fields=[
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Пришлите фото вещи',
            validator=FunctionValidator(self.validatePhoto),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Введите название вещи',
            validator=FunctionValidator(self.validateName),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Введите номер рейла',
            validator=FunctionValidator(self.validateRailNum),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Выберете ценовую политику или введите конкретную сумму',
            validator=FunctionValidator(self.validatePrice),
            on_field_entered=lambda _: None,
            buttons=[[
              InputFieldButton(
                title='Free-price',
                data=Price(type=Price.FREE),
              ),
              InputFieldButton(
                title='Платный рейл',
                data=Price(type=Price.DEFAULT_FIXED),
              )
            ]]),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Выберите категорию',
            validator=FunctionValidator(lambda o: ValidatorObject(
              success=False, error=P('Выберете категорию', emoji='fail'))),
            on_field_entered=lambda _: None,
            buttons=list_to_layout([
              InputFieldButton(
                title=category,
                data=category,
                answer='Выбрана категория "%s"' % category,
              ) for category in Category.getList()
            ])),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Введите описание вещи',
            validator=FunctionValidator(self.validateDescription),
            on_field_entered=lambda _: None,
          ),
        ],
      ))

  async def handleFind(self):
    if not self._checkTrusted():
      return

    async def articleEntered(article):
      thing = self.master.getThing(article)
      if thing is None:
        self.send(P('Такой вещи не припомню..', emoji='fail'))
      else:
        self.send(f'Рейл: {thing.rail}')
      await self.resetTgState()

    await self.setTgState(
      TgInputField(
        tg=self.tg,
        chat=self.chat,
        greeting='Введите артикул вещи',
        validator=FunctionValidator(self.validatePositive),
        on_field_entered=articleEntered,
      ))

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
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Введите артикул вещи',
            validator=ChainValidator(validators=[
              FunctionValidator(self.validatePositive),
              FunctionValidator(self.validateArticleIsExists),
            ]),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Введите номер рейла',
            validator=FunctionValidator(self.validateRailNum),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Выберете ценовую политику или введите конкретную сумму',
            validator=FunctionValidator(self.validatePrice),
            on_field_entered=lambda _: None,
            buttons=[[
              InputFieldButton(
                title='Free-price',
                data=Price(type=Price.FREE),
              ),
              InputFieldButton(
                title='Платный рейл',
                data=Price(type=Price.DEFAULT_FIXED),
              )
            ]]),
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
      TgInputField(
        tg=self.tg,
        chat=self.chat,
        greeting='Введите артикул вещи',
        validator=FunctionValidator(self.validatePositive),
        on_field_entered=articleEntered,
      ))

  async def handleSale(self):
    if not self._checkTrusted():
      return

    async def formEntered(data):
      isNotSold = data[0][0] if not self.master.sellThing(
        price=data[1],
        paymentType=data[2],
        article=data[0][0],
      ) else None
      for i in range(1, len(data[0])):
        isNotSold = data[0][i] if not self.master.removeThing(
          data[0][i]) else None
        if isNotSold:
          break
      if not isNotSold:
        self.send(P('Вещи успешно проданы!', emoji='ok'))
      else:
        self.send(P(f'На вещи {isNotSold} что-то пошло не так..', emoji='fail'))
      await self.resetTgState()

    await self.setTgState(
      TgInputForm(
        tg=self.tg,
        chat=self.chat,
        on_form_entered=formEntered,
        terminate_message='Продажа вещи прервана',
        fields=[
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Введите артикулы вещей через запятую',
            validator=ChainValidator(validators=[
              FunctionValidator(self.validateArticlesList),
              FunctionValidator(self.validateArticleIsExists),
            ]),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='За сколько продали?',
            validator=FunctionValidator(self.validatePositive),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Выберите способ оплаты',
            validator=FunctionValidator(lambda o: ValidatorObject(
              success=False, error=P('Выберите!', emoji='fail'))),
            on_field_entered=lambda _: None,
            buttons=list_to_layout([
              InputFieldButton(
                title=type,
                data=type,
              ) for type in PaymentType.getTypes()
            ]),
          ),
        ],
      ))

  async def handleSaleUntagged(self):
    if not self._checkTrusted():
      return

    async def formEntered(data):
      isSold = self.master.sellThing(price=data[0], paymentType=data[1])
      if isSold:
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
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='За сколько продали?',
            validator=FunctionValidator(self.validatePositive),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Выберите способ оплаты',
            validator=FunctionValidator(lambda o: ValidatorObject(
              success=False, error=P('Выберите!', emoji='fail'))),
            on_field_entered=lambda _: None,
            buttons=list_to_layout([
              InputFieldButton(
                title=type,
                data=type,
              ) for type in PaymentType.getTypes()
            ]),
          ),
        ],
      ))

  async def handleTotal(self):
    if not self._checkTrusted(checkGroup=True):
      return
    percent = int(self.master.getMonthlyTotal() / self.config.rent() * 100)
    timeDifference = self.master.getMonthEnd() - datetime.datetime.now()
    self.send(f"{self.master.getMonthlyTotal()}р. А это аж {percent}% от аренды. "
"До конца арендного месяца осталось {timeDifference.days}д.")

  async def handleReadd(self):
    if not self._checkTrusted():
      return
    elif not self._isDev(self.chat):
      self.send('Эта команда доступна только разработчикам.')
      return

    async def formEntered(data):
      if self.master.reAddThing(article=data[0],
                                newName=data[1],
                                newDescription=data[2]):
        self.send(P('Продукт успешно пересоздан.', emoji='ok'))
      await self.resetTgState()

    await self.setTgState(
      TgInputForm(
        tg=self.tg,
        chat=self.chat,
        on_form_entered=formEntered,
        terminate_message='Перезалив товара прерван',
        fields=[
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Введите артикул вещи',
            validator=ChainValidator(validators=[
              FunctionValidator(self.validatePositive),
              FunctionValidator(self.validateArticleIsExists),
            ]),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Введите новое название вещи',
            validator=FunctionValidator(self.validateName),
            on_field_entered=lambda _: None,
          ),
          TgInputField(
            tg=self.tg,
            chat=self.chat,
            greeting='Введите новое описание вещи',
            validator=FunctionValidator(self.validateDescription),
            on_field_entered=lambda _: None,
          ),
        ],
      ))

  # ACCESSORY
  def send(self, text):
    asyncio.create_task(send_message(tg=self.tg, chat=self.chat, text=text))

  # VALIDATORS
  @staticmethod
  def validateName(o: ValidatorObject):
    o.data = o.message.text
    if not (4 <= len(o.data) <= 64):
      o.success = False
      o.error = P(
        'Название должно быть не меньше 4 символов и не больше 64 символов',
        emoji='fail')
    return o

  @staticmethod
  def validateRailNum(o: ValidatorObject):
    o.data = o.message.text
    if not (o.data == '*' or re.match('^\d+$', o.data)):
      o.success = False
      o.error = P('Номер рейла — либо "*", либо число', emoji='fail')
    elif o.data != '*':
      o.data = str(int(o.data))
    return o

  @staticmethod
  def validateDescription(o: ValidatorObject):
    o.data = o.message.text
    if len(o.data) < 10:
      o.success = False
      o.error = P('Описание вещи должно быть минимум 10 символов', emoji='fail')
    return o

  async def validatePhoto(self, o: ValidatorObject):
    if o.message.photo is None or len(o.message.photo) < 1:
      o.success = False
      o.error = P('НУЖНО ФОТО!!', emoji='warning')
      return o
    file_id = o.message.photo[-1].file_id
    file_info = await self.tg.get_file(file_id=file_id)
    file_data = await self.tg.download_file(file_info.file_path)
    os.makedirs('photos', exist_ok=True)
    _, ext = os.path.splitext(file_info.file_path)
    file_name = 'photos/' + str(uuid.uuid4()) + ext
    with open(file_name, 'wb') as file:
      file.write(file_data)
    o.data = file_name
    return o

  @staticmethod
  def validatePrice(o: ValidatorObject):
    o.data = o.message.text
    if not re.match('^\d+$', o.data):
      o.success = False
      o.error = P('Введите положительное число', emoji='fail')
    else:
      o.data = Price(type=Price.FIXED, fixedPrice=int(o.data))
    return o

  @staticmethod
  def validatePositive(o: ValidatorObject):
    o.data = o.message.text
    if not re.match('^\d+$', o.data):
      o.success = False
      o.error = P('Введите положительное число', emoji='fail')
    else:
      o.data = int(o.data)
    return o

  @staticmethod
  def validateArticlesList(o: ValidatorObject):
    o.data = o.message.text.split(",")
    for art in o.data:
      if not re.match('^\d+$', art.strip()):
        o.success = False
        o.error = P('Введите положительные числа через запятую', emoji='fail')
        return o
    o.data = list(map(lambda x: int(x.strip()), o.data))
    return o

  def validateArticleIsExists(self, o: ValidatorObject):
    notArt = []
    if isinstance(o.data, int):
      if not self.master.getThing(o.data):
        notArt.append(str(o.data))
    else:
      for art in o.data:
        if not self.master.getThing(art):
          notArt.append(str(art))
    if notArt:
      o.success = False
      o.error = P(
        f'{"Вещи" if len(notArt) == 1 else "Вещей"} {", ".join(notArt)} не припомню..',
        emoji='fail')
    return o

  # CHECKS
  def _checkTrusted(self, checkGroup=False):
    if (self.chat.chatId in self.config.trustedUsers() or
        checkGroup and self.chat.chatId == self.config.tgGroupId()):
      return True
    self.send('Я вас не звал, идите наЬ#Я')

  def _isDev(self, chatId):
    return chatId in self.locator.config().devUsers()
