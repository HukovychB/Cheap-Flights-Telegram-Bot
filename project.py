import telebot  # type: ignore
from telebot import types
from typing import Final
import re
from datetime import datetime, date, timedelta
import pandas as pd
import schedule
from time import sleep

from scraper import find_cheap_oneway_flights

BOT_KEY: Final = "YOUR_BOT_API_KEY"
# Initiate bot
bot = telebot.TeleBot(BOT_KEY)

user_data = {}
user_states = {}
STATE_WAITING_FOR_FLIGHT_TYPE: Final = 0
STATE_WAITING_FOR_TRIP_DAYS: Final = 0.5
STATE_WAITING_FOR_DEPARTURE: Final = 1
STATE_WAITING_FOR_DESTINATION: Final = 2
STATE_WAITING_FOR_DATE: Final = 3
STATE_FINAL: Final = 4


def main():
    # Make bot work indefinitely
    bot.polling(non_stop=True)


# START COMMAND
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        f"<b>HELLO, {message.from_user.first_name.upper()}!</b>\n \nI'm going to help you find budget flights.\n \nPlease enter /search to search for tickets.",
        parse_mode="html",
    )


# SEARCH COMMAND
@bot.message_handler(commands=["search"])
def input(message):
    user_states[message.chat.id] = STATE_WAITING_FOR_FLIGHT_TYPE
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("One-way", callback_data="one-way")
    btn2 = types.InlineKeyboardButton("Round-trip", callback_data="round-trip")
    markup.row(btn1, btn2)
    bot.send_message(
        message.chat.id,
        "Do you want to search for a one-way flight or a round-trip?",
        reply_markup=markup,
    )


@bot.message_handler(commands=["stop"])
def stop(message):
    if message.chat.id in user_states and user_states[message.chat.id] == STATE_FINAL:
        bot.send_message(
            message.chat.id,
            "The automated searching is stopped.\n \nPlease enter /search to search for a different flight.",
        )
        user_states[message.chat.id] = STATE_WAITING_FOR_FLIGHT_TYPE
    else:
        bot.send_message(
            message.chat.id,
            "Automated searching was not initiated.\n\nIt can be initiated after searching for a flight using /search.",
        )


# HANDLE USER'S INPUTS AFTER THE SEARCH COMMAND WAS INITIATED
@bot.message_handler()
def handle_inputs(message):
    chat_id = message.chat.id

    if chat_id not in user_states:
        bot.send_message(chat_id, "Please use /search to start searching.")

    state = user_states[chat_id]

    if state == STATE_WAITING_FOR_TRIP_DAYS:
        try:
            user_data["Trip_days"] = int(message.text.strip())
            user_states[chat_id] = STATE_WAITING_FOR_DEPARTURE
            bot.send_message(
                chat_id,
                "Please enter your departure city in the format 'city-country' (e.g. prague-czechia, london-united-kingdom, paris-france).",
            )
        except ValueError:
            bot.send_message(
                chat_id, "You have entered wrong format. Please, enter an integer."
            )

    if state == STATE_WAITING_FOR_DEPARTURE:
        try:
            user_data["Departure"] = validate_city(message.text.strip().lower())
            user_states[chat_id] = STATE_WAITING_FOR_DESTINATION
            bot.send_message(
                chat_id,
                "Great! Now enter a destination city in the same format 'city-country' (e.g. prague-czechia, london-united-kingdom, paris-france).",
            )
        except ValueError:
            bot.send_message(
                chat_id, "You have entered wrong format. Please, try again."
            )

    elif state == STATE_WAITING_FOR_DESTINATION:
        try:
            user_data["Destination"] = validate_city(message.text.strip().lower())
            user_states[chat_id] = STATE_WAITING_FOR_DATE
            bot.send_message(
                chat_id,
                "Great! Now enter a desired departure date in the format YYYY-MM-DD (e.g. 2024-08-03) or enter 'Anytime' for flexible search.",
            )
        except ValueError:
            bot.send_message(
                chat_id,
                "You have entered wrong format or invalid date. Please, try again.",
            )

    elif state == STATE_WAITING_FOR_DATE:
        try:
            if message.text.strip().lower() == "anytime":
                user_data["Date"] = "anytime"
                user_data["Flex_date"] = ""
            else:
                user_data["Date"] = validate_date(message.text.strip())
            # Now bot will not react to any user's messages
            user_states[chat_id] = STATE_FINAL

            if user_data["Date"] != "anytime":
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("Precise", callback_data="precise")
                )
                markup.add(
                    types.InlineKeyboardButton("+-1 day", callback_data="one_day")
                )
                markup.add(
                    types.InlineKeyboardButton("+-3 days", callback_data="three_days")
                )
                markup.add(
                    types.InlineKeyboardButton("+-5 days", callback_data="five_days")
                )
                bot.send_message(
                    chat_id,
                    "Great! Do you want a precise date or it could be flexible?",
                    reply_markup=markup,
                )
            else:
                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton("Any", callback_data="any"))
                markup.add(types.InlineKeyboardButton("Direct", callback_data="direct"))
                markup.add(
                    types.InlineKeyboardButton("Up to 1 stop", callback_data="one_stop")
                )
                markup.add(
                    types.InlineKeyboardButton(
                        "Up to 2 stops", callback_data="two_stops"
                    )
                )
                bot.send_message(
                    chat_id,
                    "Great! Do you want to search for a direct fligth or not?",
                    reply_markup=markup,
                )
        except ValueError:
            bot.send_message(
                chat_id, "You have entered wrong format. Please, try again."
            )


@bot.callback_query_handler(func=lambda callback: True)
def callback_flexible_dates(callback):
    if callback.data in ["one-way", "round-trip"]:
        if callback.data == "one-way":
            user_data["Type"] = "one-way"
            user_states[callback.message.chat.id] = STATE_WAITING_FOR_DEPARTURE
            bot.send_message(
                callback.message.chat.id,
                "Please enter a departure city in the following format 'city-country' (e.g. prague-czechia, london-united-kingdom, paris-france).",
            )
        else:
            user_data["Type"] = "round-trip"
            bot.send_message(
                callback.message.chat.id,
                "Approximately how many days do you plan to stay?",
            )
            user_states[callback.message.chat.id] = STATE_WAITING_FOR_TRIP_DAYS

    if callback.data in ["precise", "one_day", "three_days", "five_days"]:
        if callback.data == "precise":
            user_data["Flex_date"] = ""
        elif callback.data == "one_day":
            user_data["Flex_date"] = "_flex1"
        elif callback.data == "three_day":
            user_data["Flex_date"] = "_flex3"
        elif callback.data == "five_days":
            user_data["Flex_date"] = "_flex5"

        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("Any", callback_data="any"))
        markup.add(types.InlineKeyboardButton("Direct", callback_data="direct"))
        markup.add(types.InlineKeyboardButton("Up to 1 stop", callback_data="one_stop"))
        markup.add(
            types.InlineKeyboardButton("Up to 2 stops", callback_data="two_stops")
        )
        bot.send_message(
            callback.message.chat.id,
            "Great! Do you want to search for a direct fligth or not?",
            reply_markup=markup,
        )

    elif callback.data in ["any", "direct", "one_stop", "two_stops"]:
        if callback.data == "any":
            user_data["Stops"] = ""
        if callback.data == "direct":
            user_data["Stops"] = "stopNumber=0~true&"
        if callback.data == "one_stop":
            user_data["Stops"] = "stopNumber=1~true&"
        if callback.data == "two_stops":
            user_data["Stops"] = "stopNumber=2~true&"
        print(user_data)
        bot.send_message(
            callback.message.chat.id,
            "Great! Let's start searching. The process may take some time. \nPlease wait......",
        )

        # -------------------------------------------------------------------------------------------
        # START SCRAPING AND DISPLAYING DATA
        # -------------------------------------------------------------------------------------------
        scrape_data(callback)

        # SET AUTOMATED REPETITION
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("1 minute", callback_data="1 minute")
        btn2 = types.InlineKeyboardButton("60 minutes", callback_data="60 minutes")
        btn3 = types.InlineKeyboardButton("12 hours", callback_data="12 hours")
        btn4 = types.InlineKeyboardButton("24 hours", callback_data="24 hours")
        markup.row(btn1, btn2)
        markup.row(btn3, btn4)
        bot.send_message(
            callback.message.chat.id,
            "If you want to set an automated repetition of this search, please select the number of minutes for the interval.\n \nOtherwise, please enter /search to search for a different flight.",
            reply_markup=markup,
        )

    elif callback.data in ["1 minute", "60 minutes", "12 hours", "24 hours"]:
        bot.send_message(
            callback.message.chat.id,
            f"Great! The automation is set.\n \nYou will see the new results in <b>{callback.data}</b>.",
            parse_mode="html",
        )
        if "minute" in callback.data:
            automation_time, _ = callback.data.split(" ")
            automation_time = int(automation_time)
        else:
            automation_time, _ = callback.data.split(" ")
            automation_time = int(automation_time) * 60
        schedule.every(automation_time).minutes.do(scrape_data, callback=callback)
        while True:
            if user_states[callback.message.chat.id] == STATE_WAITING_FOR_FLIGHT_TYPE:
                break
            schedule.run_pending()
            sleep(1)


def validate_city(city: str) -> str:
    if re.match(r"^([a-z]+-[a-z]+)+$", city):
        return city
    else:
        raise ValueError("Invalid city format")


def validate_date(date_str: str) -> str:
    input_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    if date.today() <= input_date:
        return date_str
    else:
        raise ValueError


def transform_dates(date_str: str, shift_days: int) -> str:
    try:
        date_obj = datetime.strptime(date_str, "%a %d %b")
        date_obj = date_obj.replace(year=datetime.now().year)

        if datetime.now() > date_obj:
            date_obj = date_obj.replace(year=datetime.now().year + 1)

        new_date_obj = date_obj + timedelta(days=shift_days)
        return new_date_obj.strftime("%Y-%m-%d")

    except ValueError:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        new_date_obj = date_obj + timedelta(days=shift_days)
        return new_date_obj.strftime("%Y-%m-%d")


def scrape_data(callback):
    try:
        # Find departure data
        first_flight_data = find_cheap_oneway_flights(user_data)[0:5]

        # -----------------------------------------------------------------
        # ONE-WAY OPTION
        # -----------------------------------------------------------------
        if user_data["Type"] == "one-way":
            for index, row in pd.DataFrame(first_flight_data).iterrows():
                airlines = ", ".join(row["airline"])
                if "date" in row:
                    bot.send_message(
                        callback.message.chat.id,
                        f"<b>{index+1}</b>.\n <b>Price:            <i>{row['price']}</i></b>\n <b>Date:</b>            {row['date']}\n <b>Departure:</b> {row['departure_time']}\n <b>Arrival:</b>        {row['arrival_time']}\n <b>Airlines:</b>       {airlines}\n <b>Stops:</b>           {row['stops']}",
                        parse_mode="html",
                    )
                else:
                    bot.send_message(
                        callback.message.chat.id,
                        f"<b>{index+1}</b>.\n <b>Price:            <i>{row['price']}</i></b>\n <b>Date:</b>            {user_data['Date']}\n <b>Departure:</b> {row['departure_time']}\n <b>Arrival:</b>        {row['arrival_time']}\n <b>Airlines:</b>       {airlines}\n <b>Stops:</b>           {row['stops']}",
                        parse_mode="html",
                    )

        # -----------------------------------------------------------------
        # ROUND-TRIP OPTION
        # -----------------------------------------------------------------
        elif user_data["Type"] == "round-trip":
            # In case user inputs a precise date of departure
            if user_data["Flex_date"] == "" and user_data["Date"] != "anytime":
                days = int(user_data["Trip_days"])
                return_date = transform_dates(user_data["Date"], days)

                return_user_data = user_data.copy()
                return_user_data["Date"] = return_date
                return_user_data["Flex_date"] = "_flex1"
                return_user_data["Destination"] = user_data["Departure"]
                return_user_data["Departure"] = user_data["Destination"]
                list_return_flights = find_cheap_oneway_flights(return_user_data)[0:5]

            else:
                sent_message = bot.send_message(
                    callback.message.chat.id, "0% FINISHED"
                ).message_id
                days = int(user_data["Trip_days"])
                first_flight_date = pd.DataFrame(first_flight_data)["date"]
                transformed_dates = first_flight_date.apply(
                    lambda x: transform_dates(x, days)
                )
                return_user_data = user_data.copy()
                list_return_flights = []
                percent_finished = 0
                for dates in transformed_dates:
                    return_user_data["Date"] = dates
                    return_user_data["Flex_date"] = "_flex1"
                    return_user_data["Destination"] = user_data["Departure"]
                    return_user_data["Departure"] = user_data["Destination"]
                    second_flight_data = find_cheap_oneway_flights(return_user_data)[0]
                    list_return_flights.append(second_flight_data)
                    percent_finished += 20
                    bot.delete_message(callback.message.chat.id, sent_message)
                    sent_message = bot.send_message(
                        callback.message.chat.id, f"{percent_finished}% FINISHED"
                    ).message_id

                bot.delete_message(callback.message.chat.id, sent_message)

            combined_flight_data = list(zip(first_flight_data, list_return_flights))

            for index, (first, second) in enumerate(combined_flight_data):
                airlines_first = ", ".join(first["airline"])
                airlines_second = ", ".join(second["airline"])
                total_price = int(
                    first["price"].replace(" Kč", "").replace(",", "")
                ) + int(second["price"].replace(" Kč", "").replace(",", ""))
                if "date" in first and "date" in second:
                    bot.send_message(
                        callback.message.chat.id,
                        f"<b>{index+1}</b>.\n <b>Departing flight:</b>\n <b>Price:            <i>{first['price']}</i></b>\n <b>Date:</b>            {first['date']}\n <b>Departure:</b> {first['departure_time']}\n <b>Arrival:</b>        {first['arrival_time']}\n <b>Airlines:</b>       {airlines_first}\n <b>Stops:</b>           {first['stops']}\n \n <b>Return flight:</b>\n <b>Price:            <i>{second['price']}</i></b>\n <b>Date:</b>            {second['date']}\n <b>Departure:</b> {second['departure_time']}\n <b>Arrival:</b>        {second['arrival_time']}\n <b>Airlines:</b>       {airlines_second}\n <b>Stops:</b>           {second['stops']}\n \n <b>TOTAL PRICE: {total_price} Kč</b>",
                        parse_mode="html",
                    )
                else:
                    bot.send_message(
                        callback.message.chat.id,
                        f"<b>{index+1}</b>.\n <b>Departing flight:</b>\n <b>Price:            <i>{first['price']}</i></b>\n <b>Date:</b>            {user_data['Date']}\n <b>Departure:</b> {first['departure_time']}\n <b>Arrival:</b>        {first['arrival_time']}\n <b>Airlines:</b>       {airlines_first}\n <b>Stops:</b>           {first['stops']}\n \n <b>Return flight:</b>\n <b>Price:            <i>{second['price']}</i></b>\n <b>Date:</b>            {return_user_data['Date']}\n <b>Departure:</b> {second['departure_time']}\n <b>Arrival:</b>        {second['arrival_time']}\n <b>Airlines:</b>       {airlines_second}\n <b>Stops:</b>           {second['stops']}\n \n <b>TOTAL PRICE: {total_price} Kč</b>",
                        parse_mode="html",
                    )

    except Exception:
        bot.send_message(
            callback.message.chat.id,
            "An error occured. Please try to input something different. Type /search to start over.",
        )


if __name__ == "__main__":
    main()
