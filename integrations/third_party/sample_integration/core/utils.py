import datetime as dt
from collections.abc import Iterator


def date_range(start_date: dt.date, end_date: dt.date) -> Iterator[dt.date]:
    """Generator function to iterate over a range of dates."""
    current_date = start_date
    while current_date <= end_date:
        yield current_date
        current_date += dt.timedelta(days=1)
