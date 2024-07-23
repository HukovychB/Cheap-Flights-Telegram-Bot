from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
from typing import List, Dict
from tabulate import tabulate

driver = None


# SCRAPER
def find_cheap_oneway_flights(flight_info: dict) -> List[Dict]:
    global driver
    driver = webdriver.Chrome()
    url = f"https://www.kiwi.com/en/search/results/{flight_info['Departure']}/{flight_info['Destination']}/{flight_info['Date']}{flight_info['Flex_date']}/no-return?{flight_info['Stops']}sortBy=price"
    try:
        # Open the URL
        driver.get(url)

        # Close the pop-up cookie window
        click_smth('//button[@data-test="CookiesPopup-Accept"]')

        # Let the page load
        sleep(5)

        # Click on CHEAPEST
        click_smth('//button[@data-test="SortBy-price"]')

        # Select flight cards
        flights_data = extract_flight_data(flight_info)

        # sleep(5)
    except TimeoutException as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        driver.quit()

    return flights_data


def click_smth(xpath: str) -> None:
    accept_cookies_xpath = xpath
    cookies_element = WebDriverWait(driver, 5).until(
        EC.element_to_be_clickable((By.XPATH, accept_cookies_xpath))
    )
    sleep(1)
    cookies_element.click()


def extract_flight_data(flight_info) -> List[Dict]:
    # Select flight cards
    flight_cards = driver.find_elements(
        "xpath", '//div[@data-test="ResultCardWrapper"]'
    )

    flights_data: list = []

    for card in flight_cards:
        element_dict: dict = {}
        elementHTML = card.get_attribute("outerHTML")
        elementSoup = BeautifulSoup(elementHTML, "html.parser")

        # Extract prices
        price_section = elementSoup.find("div", {"data-test": "ResultCardPrice"})
        price = price_section.find("span")
        element_dict["price"] = price.text.replace("\xa0", " ")

        # Extract date
        if flight_info["Date"] == "anytime" or flight_info["Flex_date"] != "":
            date_section = elementSoup.find(
                "p", {"data-test": "ResultCardSectorDepartureDate"}
            )
            date = date_section.find("time")
            element_dict["date"] = date.text

        # Extract departure date
        time_section = elementSoup.find_all("div", {"data-test": "TripTimestamp"})
        timestamps = [div.find("time").text for div in time_section]
        element_dict["departure_time"] = timestamps[0]
        element_dict["arrival_time"] = timestamps[1]

        # Extract airlines
        # airline_section = elementSoup.find("div", {"class": "orbit-carrier-logo flex content-between justify-between bg-transparent flex-row w-icon-large h-icon-large"})
        # airline = airline_section.find("img")
        # element_dict["airline"] = airline.get('title')

        airline_section = elementSoup.find(
            "div", {"class": "flex flex-wrap items-center justify-center gap-y-xxs"}
        )
        airlines_images = airline_section.find_all("img")
        airlines = [img.get("title") for img in airlines_images]
        element_dict["airline"] = airlines

        # Extract the number of stops
        stops = elementSoup.find("div", {"class": "py-xxs px-0 leading-none"})
        element_dict["stops"] = stops.text

        # Append to the list
        flights_data.append(element_dict)

    return flights_data


if __name__ == "__main__":
    flight_info: dict = {
        "Departure": "prague-czechia",
        "Destination": "new-york-city-new-york-united-states",
        "Date": "2024-08-03",
        "Flex_date": "",
        "Stops": "stopNumber=1~true&",
    }
    df = pd.DataFrame(find_cheap_oneway_flights(flight_info))
    print(tabulate(df, headers=df.columns, tablefmt="grid"))
