import datetime as dt


def datetime_copy_with(
  val: dt.datetime,
  year: int = None,
  month: int = None,
  day: int = None,
  hour: int = None,
  minute: int = None,
  second: int = None,
  microsecond: int = None,
):
  return dt.datetime(
    year=val.year if year is None else year,
    month=val.month if month is None else month,
    day=val.day if day is None else day,
    hour=val.hour if hour is None else hour,
    minute=val.minute if minute is None else minute,
    second=val.second if second is None else second,
    microsecond=val.microsecond if microsecond is None else microsecond,
  )


def is_today(timestamp: dt.datetime):
  return is_same_day(dt.datetime.today(), timestamp)


def is_same_day(one: dt.datetime, two: dt.datetime):
  return (one.year, one.month, one.day) == (two.year, two.month, two.day)
