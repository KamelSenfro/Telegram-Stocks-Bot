import os
import telebot
import yfinance as yf

# Set your Telegram Bot API Key
API_KEY = 'ItExpired'
bot = telebot.TeleBot(API_KEY)

# Define command handlers

# Welcome message handler
@bot.message_handler(commands=['start', 'help', 'hi', 'hello'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Welcome to the Stock Price Bot. Use /wsb for popular stocks or type 'price [ticker]' to get the current price of any stock.")

# Handler for the /wsb command to get stock prices of popular stocks
@bot.message_handler(commands=['wsb'])
def get_stocks(message):
    response = ""
    stocks = ['GME', 'AMC', 'NOK']  # Popular stocks
    stock_data = {}
    
    # Fetch stock data for each stock
    for stock in stocks:
        try:
            data = yf.download(tickers=stock, period='2d', interval='1d')
            data = data.reset_index()
            stock_data[stock] = data
        except Exception as e:
            bot.send_message(message.chat.id, f"Error fetching data for {stock}: {e}")
            return

    # Construct response message
    response = "Stock Prices:\n"
    for stock, data in stock_data.items():
        response += f"----- {stock} -----\n"
        for index, row in data.iterrows():
            price = round(row['Close'], 2)
            formatted_date = row['Date'].strftime('%m/%d')
            response += f"{formatted_date}: ${price}\n"
        response += "\n"

    # Send response message to user
    bot.send_message(message.chat.id, response)

# Function to determine if the message is a stock price request
def stock_request(message):
    request = message.text.split()
    return len(request) == 2 and request[0].lower() == "price"

# Handler for stock price requests
@bot.message_handler(func=stock_request)
def send_price(message):
    request = message.text.split()[1].upper()  # Extract stock ticker from message
    try:
        data = yf.download(tickers=request, period='1d', interval='1m')  # Fetch stock data
        if not data.empty:
            data = data.reset_index()
            data["format_date"] = data['Datetime'].dt.strftime('%m/%d %I:%M %p')
            latest_price = round(data['Close'].iloc[-1], 2)  # Get latest price
            response = f"Latest price for {request}: ${latest_price}\n"
            response += "Price history:\n"
            for index, row in data.iterrows():
                response += f"{row['format_date']}: ${round(row['Close'], 2)}\n"
            # Send response message to user
            bot.send_message(message.chat.id, response)
        else:
            # Send message if no data is available
            bot.send_message(message.chat.id, "No data available for the given ticker.")
    except Exception as e:
        # Handle any exceptions and notify the user
        bot.send_message(message.chat.id, f"Error fetching data for {request}: {e}")

# Start polling for messages
bot.polling()
