from typing import Optional, List

from src.domain.locator import LocatorStorage
from src.domain.thing import Thing


class Repo(LocatorStorage):
  ARTICLE_ITERATOR = 'ARTICLE_ITERATOR'
  THING_CATEGORY = 'THING_CATEGORY'
  
  def __init__(self, locator):
    super().__init__(locator)
    self.lira = self.locator.lira()
    self.articleIterator = self.lira.get(Repo.ARTICLE_ITERATOR, 0)

  def addThing(self, thing: Thing):
    if thing.article is None:
      raise Exception('Repo::addThing() -> article is None')
    self.lira.put(obj=thing, id=thing.article, cat=Repo.THING_CATEGORY)
    self.lira.flush()
  
  def removeThing(self, article: int) -> Thing:
    thing = self.lira.pop(id=article)
    self.lira.flush()
    return thing
  
  def getThing(self, article: int) -> Optional[Thing]:
    return self.lira.get(id=article)
  
  def updateThing(self, thing: Thing):
    self.addThing(thing)
  
  def makeNextArticle(self) -> int:
    article = self.articleIterator
    self.articleIterator += 1
    self.lira.put(self.articleIterator, id=Repo.ARTICLE_ITERATOR)
    self.lira.flush()
    return article
  
  def getAllThings(self) -> List[Thing]:
    return list(map(lambda id: self.lira.get(id),
                    self.lira[Repo.THING_CATEGORY]))