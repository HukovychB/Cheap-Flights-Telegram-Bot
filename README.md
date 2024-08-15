# Cheap Flights Telegram Bot

#### Video Demo:  https://youtu.be/O9-yEv3KMIs
#### Website Page:  https://hukovychb.github.io/project_pages/telegram-flight-bot
## Overview

This Telegram bot helps users find budget flights using web scraping. It interacts with users to collect flight search parameters, performs the search using a scraping script, and presents the results within Telegram. The bot can handle one-way and round-trip flights and allows users to specify flexible travel dates and type of flights (direct or with stops). Finally, it allows users to set an automated search that is conducted at specified time interval.

## Features

- **Search for one-way or round-trip flights**: Users can choose between one-way and round-trip flight searches.
- **Flexible date search**: Users can specify exact dates or allow for more flexible travel dates including an option "Anytime".
- **Filter by stops**: Users can choose between direct flights, flights with one stop, or flights with up to two stops.
- **Automated search repetition**: Users can set up automated searches at regular intervals.
- **Display all relevant information about the cheapest flights**: The search results are sorted by price and display information such as price, departure date, departure time, arrival time, airlines and number of stops.

## Requirements

- Selenium
- BeautifulSoup
- Pandas
- Telebot
- Schedule
- Tabulate

## Setup

### 1. Install Dependencies

Make sure you have Python installed, then install the required Python libraries using pip:

```bash
pip install -r requirements.txt
```
### 2. Download ChromeDriver
Download ChromeDriver that matches your version of Google Chrome from ChromeDriver download page. Place the chromedriver executable in your system's PATH or in the project directory.

### 3. Configure the Bot
Replace the BOT_KEY placeholder with your actual Telegram bot API key. You can obtain this key by creating a bot on Telegram via BotFather.

In the bot.py file, replace:

```bash
BOT_KEY: Final = "YOUR_BOT_API_KEY"
```
with your actual bot API key that you can obtain from *@BotFather* within Telegram.

### 4. Running the Bot
To start the bot, simply run the following command:
```bash
python project.py
```
The bot will be working until it is stopped in the terminal.

## How to use

### Start the Bot
To start using the bot, send the */start* command to the bot in Telegram. It will provide instructions on how to begin a flight search.

### Search for Flights
1. **Initiate Search**: Send the */search* command.
2. **Choose Flight Type**: Select between "One-way" or "Round-trip".
3. **Enter Details**:
    - **Departure city**: format: city-country
    - **Destination city** format: city-country
    - **Desired departure date**: format YYYY-MM-DD or "Anytime" for flexible dates
    - **Specify Stops**: Choose between direct flights, flights with one stop, or flights with up to two stops.
4. **Receive Results**: The bot will scrape flight data and send the results. You can also set automated search repetition if desired.

## Code Structure

### **'scraper.py'**
This file contains functions for scraping flight data using Selenium and BeautifulSoup. Key functions include:

 - **find_cheap_oneway_flights(flight_info: dict) -> List[Dict]**: Finds and returns a list of cheap one-way flights based on the provided search parameters.

### **'project.py'**

This file sets up and manages the Telegram bot using Telebot. It handles user interactions and coordinates with the scraper to provide flight search results. Key components include:

- Command handlers for */start, /search, and /stop*.
- Callback handlers for user interactions during the search process.
- Functions for validating input and managing automated search repetition.

## Licence
This project is licensed and prohibits any distribution or commercial use. See the [LICENCE](LICENCE.htm) file for details.
