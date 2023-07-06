from typing import Optional

from vk_api import VkUpload, ApiError

from src.domain.locator import LocatorStorage, Locator
from src.domain.models.thing import Thing, Price, Category


class Vk(LocatorStorage):

  def __init__(self, locator: Locator):
    super().__init__(locator)
    self.config = self.locator.config()
    self.vk = self.locator.vkApi()
    self.api = self.vk.get_api()
    self.upload = VkUpload(self.api)
    self.groupId = self.config.vkGroupId()

  def makePost(self, text: str):
    self.api.wall.post(
      owner_id=self.groupId,
      message=text,
      from_group=1,
    )

  def addProduct(self, thing: Thing = None) -> Optional[int]:
    """return vkId"""
    try:
      response = self.upload.photo_market(
        photo=thing.photoFilename,
        group_id=self.groupId,
        main_photo=True,
      )
      photo_id = response[0]['id']
      response = self.api.market.add(
        owner_id=self.groupId,
        name=thing.name,
        description=thing.description,
        category_id=thing.vkCategory,
        main_photo_id=photo_id,
        sku=str(thing.article),
        price=self._getPrice(thing.price),
      )
      thing.vkId = int(response['market_item_id'])
    except ApiError as e:
      self.locator.logger().error(f'Vk::addProduct() -> {e}')
      return None
    try:
      self.api.market.addToAlbum(
        owner_id=self.groupId,
        item_ids=str(thing.vkId),
        album_ids=str(category2vkAlbumId(thing.category)),
      )
    except Exception as e:
      print(e)
    return thing.vkId

  def updateProduct(self, thing: Thing):
    """without photo"""
    self.api.market.edit(
      item_id=thing.vkId,
      owner_id=self.groupId,
      name=thing.name,
      description=thing.description,
      category_id=thing.vkCategory,
      sku=str(thing.article),
      price=self._getPrice(thing.price),
    )

  def removeProduct(self, vkId: int):
    self.api.market.delete(
      item_id=vkId,
      owner_id=self.groupId,
    )

  def _getPrice(self, price: Price) -> int:
    if price.type == Price.FREE:
      return self.config.defaultFreePrice()
    elif price.type == Price.DEFAULT_FIXED:
      return self.config.defaultFixedPrice()
    else:
      return price.fixedPrice


def category2vkAlbumId(cat: str) -> Optional[int]:
  return {
    Category.UP: 2,
    Category.DOWN: 3,
    Category.FULL: 4,
    Category.SHOES: 5,
    Category.ACCESSORIES: 6,
    Category.BOOKS: 7,
    Category.OTHER: 8,
  }.get(cat, None)
