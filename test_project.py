from project import validate_city, validate_date, transform_dates

import pytest
from datetime import date, timedelta, datetime


def test_validate_city():
    input = {
        "prague-czechia":"prague-czechia",
        "london-united-kingdom":"london-united-kingdom",
        "los-angeles-california-united-states":"los-angeles-california-united-states",
        "new-york-city-new-york-united-states":"new-york-city-new-york-united-states",
        "paris-france":"paris-france",
    }
    for k,v in input.items():
        assert validate_city(k) == v

    with pytest.raises(ValueError):
        validate_city("fdsfsfsf")
    with pytest.raises(ValueError):
        validate_city("prague-czech1a")
    with pytest.raises(ValueError):
        validate_city("prague czechia")
    with pytest.raises(ValueError):
        validate_city("pragueczechia")


def test_validate_date():
    input = {
        "2100-02-03":"2100-02-03",
        str(date.today()):str(date.today()),
        str(date.today()+timedelta(1)):str(date.today()+timedelta(1)),
    }
    for k,v in input.items():
        assert validate_date(k) == v

    with pytest.raises(ValueError):
        validate_date("2024/08/03")
    with pytest.raises(ValueError):
        validate_date("September 8, 2024")
    with pytest.raises(ValueError):
        validate_date("fdsfdfsdfs")


def test_transform_dates():
    assert transform_dates('2024-07-01', 5) == '2024-07-06'
    assert transform_dates('2024-07-01', -5) == '2024-06-26'

    assert transform_dates('2024-07-01', 0) == '2024-07-01'

