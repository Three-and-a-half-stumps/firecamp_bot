class Command:

  def __init__(
    self,
    name: str,
    preview: str,
    description: str,
    handler: str,
    addToMenu: bool = False,
  ):
    self.name = name
    self.preview = preview
    self.description = description
    self.handler = handler
    self.addToMenu = addToMenu


global_command_list = [
  Command(*args) for args in [
    (
      'start',
      '/start',
      '',
      'handleStart',
    ),
    (
      'new',
      '/new',
      'Добавить вещь',
      'handleNew',
      True,
    ),
    (
      'newnew',
      '/newnew',
      'Добавить новую-новую вещь',
      'handleNewNew',
      False,
    ),
    (
      'find',
      '/find',
      'Найти рейл вещи',
      'handleFind',
      True,
    ),
    (
      'move',
      '/move',
      'Перевесить вещь',
      'handleMove',
      True,
    ),
    (
      'sale',
      '/sale',
      'Продать вещь',
      'handleSale',
      True,
    ),
    (
      'sale_untagged',
      '/sale_untagged',
      'Продать вещь без бирки',
      'handleSaleUntagged',
      True,
    ),
    (
      'delete',
      '/delete',
      'Выбросить вещь',
      'handleDelete',
      True,
    ),
    (
      'total',
      '/total',
      'Узнать приход в текущем месяце',
      'handleTotal',
      True,
    ),
    (
      'count_things',
      '/count_things',
      'Узнать количество всех вещей',
      'handleCountThings',
      True,
    ),
    (
      'count_things_on_rail',
      '/count_things_on_rail',
      'Узнать количество вещей на рейле',
      'handleCountThingsOnRail',
      True,
    ),
  ]
]
