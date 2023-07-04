from typing import Callable, Any, Union, List
import datetime as dt

from src.domain.locator import LocatorStorage, Locator
from src.domain.models.thing import Price, Category
from src.managers.sheet.sheet import PaymentType
from src.utils.tg.piece import P, Pieces
from src.utils.tg.tg_destination import TgDestination
from src.utils.tg.tg_input_field import TgInputField, InputFieldButton
from src.utils.tg.utils import list_to_layout
from src.utils.tg.value_validators import ChainValidator


class InputFieldsConstructor(LocatorStorage):

  def __init__(self, locator: Locator):
    super().__init__(locator)

  def chat(self, chat: TgDestination):
    return InputFieldsConstructorParameterized(self.locator, chat)


class InputFieldsConstructorParameterized(LocatorStorage):

  def __init__(self, locator: Locator, chat: TgDestination):
    super().__init__(locator)
    self.tg = self.locator.tg()
    self.validators = self.locator.validatorsConstructor()
    self.chat = chat

  # Common fields
  def naturalInt(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[str], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Введите натуральное число',
      validator=self.validators.naturalInt(),
      on_field_entered=onEntered,
    )

  # Thing fields
  def thingPhoto(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[str], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Пришлите фото вещи',
      validator=self.validators.photoFromTelegram(),
      on_field_entered=onEntered,
    )

  def thingName(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[str], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Введите название вещи',
      validator=self.validators.thingName(),
      on_field_entered=onEntered,
    )

  def thingRailNum(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[str], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Введите номер рейла',
      validator=self.validators.thingRailNum(),
      on_field_entered=onEntered,
    )

  def thingPricePolicy(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[Price], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or
      'Выберете ценовую политику или введите конкретную сумму',
      validator=self.validators.thingPrice(),
      on_field_entered=onEntered,
      buttons=[[
        InputFieldButton(
          title='Free-price',
          data=Price(type=Price.FREE),
        ),
        InputFieldButton(
          title='Платный рейл',
          data=Price(type=Price.DEFAULT_FIXED),
        )
      ]],
    )

  def thingCateogry(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[str], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Выберете категорию',
      validator=self.validators.errorValidator(err=P(
        'Выберете категорию',
        emoji='fail',
      )),
      on_field_entered=onEntered,
      buttons=list_to_layout([
        InputFieldButton(
          title=category,
          data=category,
          answer='Выбрана категория "%s"' % category,
        ) for category in Category.getList()
      ]),
    )

  def thingDescription(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[str], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Введите описание вещи',
      validator=self.validators.thingDescription(),
      on_field_entered=onEntered,
    )

  def existedThingArticle(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[int], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Введите артикул вещи',
      validator=ChainValidator(validators=[
        self.validators.naturalInt(),
        self.validators.thingArticlesIsExists(),
      ]),
      on_field_entered=onEntered,
    )

  def existedThingArticleList(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[List[int]], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Введите артикулы вещей через запятую',
      validator=ChainValidator(validators=[
        self.validators.naturalIntList(),
        self.validators.thingArticlesIsExists(),
      ]),
      on_field_entered=onEntered,
    )

  def thingPaymentType(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[str], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Выберите способ оплаты',
      validator=self.validators.errorValidator(err=P(
        'Выберите!',
        emoji='fail',
      )),
      on_field_entered=onEntered,
      buttons=list_to_layout([
        InputFieldButton(
          title=type,
          data=type,
        ) for type in PaymentType.getTypes()
      ]),
    )

  def thingDatatime(
    self,
    greeting: Union[str, Pieces] = None,
    onEntered: Callable[[str], Any] = lambda _: None,
  ) -> TgInputField:
    return TgInputField(
      tg=self.tg,
      chat=self.chat,
      greeting=greeting or 'Введите дату появления вещи или введите',
      validator=self.validators.correctDatatime(),
      on_field_entered=onEntered,
      buttons=list_to_layout([
        InputFieldButton(
          title='Сегодня',
          data=dt.datetime.today(),
        ),
        InputFieldButton(
          title='Вчера',
          data=dt.datetime(
            year=dt.datetime.today().year,
            month=dt.datetime.today().month,
            day=dt.datetime.today().day - 1
          ),
        )
      ]),
    )