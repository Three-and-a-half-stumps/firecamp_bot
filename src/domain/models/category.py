from typing import Any, Dict


class Category:

  @staticmethod
  def fromJson(json: Dict[str, Any]):
    return Category(
      buttonTitle=json['button_title'],
      vkAlbumId=json['vk_album_id'],
      defaultExpirationDaysCount=json['default_expiration_days_count'],
      internalId=json['internal_id'],
    )

  def __init__(
    self,
    buttonTitle: str,
    vkAlbumId: int,
    defaultExpirationDaysCount: int,
    internalId: int,
  ):
    self.buttonTitle = buttonTitle
    self.vkAlbumId = vkAlbumId
    self.defaultExpirationDaysCount = defaultExpirationDaysCount
    self.internalId = internalId

  def __repr__(self):
    return f'<Category: {self.__dict__}>'
