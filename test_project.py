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
    current_year = datetime.now().year
    next_year = datetime.now().year + 1

    input = {
        "Mon 18 Nov":f"{current_year}-11-23",
        "Mon 9 Sep":f"{current_year}-09-14",
        "Tue 26 Nov":f"{current_year}-12-01",
    }
    for k,v in input.items():
        assert transform_dates(k, 5, year = "current") == v
    
    input = {
        "Mon 18 Nov":f"{next_year}-11-23",
        "Mon 9 Sep":f"{next_year}-09-14",
        "Tue 26 Nov":f"{next_year}-12-01",
    }
    for k,v in input.items():
        assert transform_dates(k, 5, year = "next") == v

    input = {
        f"{current_year}-08-03":f"{current_year}-08-08",
        f"{current_year}-05-20":f"{current_year}-05-25",
    }
    for k,v in input.items():
        assert transform_dates(k, 5, year = "current") == v


