from typing import Optional, List

from src.domain.locator import LocatorStorage
from src.domain.models.thing import Thing


class Repo(LocatorStorage):
  ARTICLE_ITERATOR = 'ARTICLE_ITERATOR'

  def __init__(self, locator):
    super().__init__(locator)
    self.thingsRepo = self.locator.thingsRepo()
    self.lira = self.locator.lira()
    self.articleIterator = self.lira.get(Repo.ARTICLE_ITERATOR, 0)

  def addThing(self, thing: Thing):
    if thing.article is None:
      raise Exception('Repo::addThing() -> article is None')
    self.thingsRepo.put(thing)

  def removeThing(self, article: int) -> Thing:
    return self.thingsRepo.remove(article)

  def getThing(self, article: int) -> Optional[Thing]:
    return self.thingsRepo.find(article)

  def makeNextArticle(self) -> int:
    article = self.articleIterator
    self.articleIterator += 1
    self.lira.put(self.articleIterator, id=Repo.ARTICLE_ITERATOR)
    self.lira.flush()
    return article

  def getThingsOnRail(self, rail: int) -> List[Thing]:
    return self.thingsRepo.findAll(lambda thing: thing.rail == rail)

  def getAllThings(self) -> List[Thing]:
    return self.thingsRepo.findAll()
