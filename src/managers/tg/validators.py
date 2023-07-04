import os
import re
import uuid
import datetime as dt
from typing import Callable

from src.domain.locator import LocatorStorage, Locator
from src.domain.models.thing import Price
from src.utils.tg.piece import P, Pieces
from src.utils.tg.value_validators import ValidatorObject, Validator, \
  FunctionValidator


class ValidatorsConstructor(LocatorStorage):

  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.tg = self.locator.tg()
    self.config = self.locator.config()
    self.logger = self.locator.logger()

  # Common validators
  def naturalInt(self, err: Pieces = None) -> Validator:
    """
    На выходе в obj.data имеем int >= 0
    """

    def validateNatural(o: ValidatorObject):
      o.data = o.message.text
      if not re.match('^\d+$', o.data):
        o.success = False
        o.error = err or P('Введите натуральное число', emoji='fail')
      else:
        o.data = int(o.data)
      return o

    return self._handleExceptionWrapper(validateNatural)

  def naturalIntList(self, err: Pieces = None) -> Validator:
    """
    На выходе в obj.data имеем List[int]
    """

    def validateArticlesList(o: ValidatorObject):
      o.data = o.message.text.split(",")
      for art in o.data:
        if not re.match('^\d+$', art.strip()):
          o.success = False
          o.error = err or P(
            'Введите натуральные числа через запятую',
            emoji='fail',
          )
          return o
      o.data = [int(x.strip()) for x in o.data]
      return o

    return self._handleExceptionWrapper(validateArticlesList)

  def correctDatatime(self, err: Pieces = None) -> Validator:

    def validateParseDatatime(o: ValidatorObject):
      formats = [
        '%d %B',
        '%d.%m'
      ]
      for fmt in formats:
        try:
          date = dt.datetime.strptime(o.message.text, fmt)
          o.data = dt.datetime(year=dt.datetime.today().year, month=date.month, day=date.day)
          return o
        except:
          continue
      o.success = False
      o.error = err or (P('Не получилось считать дату время '
                                  'Введите время в одном из следующих форматов:\n') +
                              P('\n'.join([dt.datetime.now().strftime(fmt) for fmt in formats]),
                                  types='code'))
      return o


    return self._handleExceptionWrapper(validateParseDatatime)

  def errorValidator(self, err: Pieces = None) -> Validator:
    return self._handleExceptionWrapper(lambda o: ValidatorObject(
      message=o.message,
      success=False,
      error=err or P('Ошибка :(', emoji='fail'),
    ))

  # Telegram validators
  def photoFromTelegram(self) -> Validator:
    """
    На выходе в obj.data имеем str (имя файла с изображением)
    """

    async def validatePhoto(o: ValidatorObject):
      if o.message.photo is None or len(o.message.photo) < 1:
        o.success = False
        o.error = P('НУЖНО ФОТО!!', emoji='warning')
        return o
      try:
        file_id = o.message.photo[-1].file_id
        file_info = await self.tg.get_file(file_id=file_id)
        file_data = await self.tg.download_file(file_info.file_path)
        os.makedirs(self.config.photoDir(), exist_ok=True)
        _, ext = os.path.splitext(file_info.file_path)
        file_name = f'{self.config.photoDir()}/' + str(uuid.uuid4()) + ext
        with open(file_name, 'wb') as file:
          file.write(file_data)
        o.data = file_name
      except Exception as e:
        o.success = False
        o.error = P(
          'Почему-то не поулчилось загрузить изображение :( Текст ошибки: ',
          emoji='fail',
        ) + P(str(e), types='code')
        self.logger.error(str(e))
      return o

    return self._handleExceptionWrapper(validatePhoto)

  # Thing validators
  def thingName(self) -> Validator:
    """
    На выходе в obj.data имеем str: 4 <= len(obj.data) <= 64
    """

    def validateName(o: ValidatorObject):
      o.data = o.message.text
      if not (4 <= len(o.data) <= 64):
        o.success = False
        o.error = P(
          'Название должно быть не меньше 4 символов и не больше 64 символов',
          emoji='fail',
        )
      return o

    return self._handleExceptionWrapper(validateName)

  def thingRailNum(self) -> Validator:
    """
    На выходе в obj.data имеем str: либо '*' либо натуральное число (но тоже в
    str)
    """

    def validateRailNum(o: ValidatorObject):
      o.data = o.message.text
      if not (o.data == '*' or re.match(r'^\d+$', o.data)):
        o.success = False
        o.error = P('Номер рейла — либо "*", либо число', emoji='fail')
      elif o.data != '*':
        o.data = str(int(o.data))
      return o

    return self._handleExceptionWrapper(validateRailNum)

  def thingPrice(self) -> Validator:
    """
    На выходе в obj.data имеем Price
    """

    def validatePrice(o: ValidatorObject):
      o.data = o.message.text
      if not re.match('^\d+$', o.data):
        o.success = False
        o.error = P('Введите натуральное число', emoji='fail')
      else:
        o.data = Price(type=Price.FIXED, fixedPrice=int(o.data))
      return o

    return self._handleExceptionWrapper(validatePrice)

  def thingDescription(self) -> Validator:
    """
    На выходе в obj.data имеем str: len(obj.data) >= 10
    """

    def validateDescription(o: ValidatorObject):
      o.data = o.message.text
      if len(o.data) < 10:
        o.success = False
        o.error = P(
          'Описание вещи должно быть минимум 10 символов',
          emoji='fail',
        )
      return o

    return self._handleExceptionWrapper(validateDescription)

  def thingArticlesIsExists(self) -> Validator:

    def validate(o: ValidatorObject):
      master = self.locator.master()
      missing = []
      if isinstance(o.data, int):
        if master.getThing(o.data) is None:
          missing.append(str(o.data))
      else:
        for art in o.data:
          if master.getThing(art) is None:
            missing.append(str(art))
      if len(missing) > 0:
        o.success = False
        o.error = P(
          f'{"Вещи" if len(missing) == 1 else "Вещей"} '
          f'{", ".join(missing)} не припомню..',
          emoji='fail',
        )
      return o

    return self._handleExceptionWrapper(validate)

  # Accessory
  def _handleExceptionWrapper(self, validateFunciton: Callable) -> Validator:

    def validate(o: ValidatorObject):
      try:
        o = validateFunciton(o)
      except Exception as e:
        o.error = P(
          'При проверке значения что-то пошло не так :( Текст ошибки: ',
          emoji='fail',
        ) + P(str(e), types='code')
        self.logger.error(str(e))
      return o

    return FunctionValidator(validate)
