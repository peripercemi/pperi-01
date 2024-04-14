import tkinter as tk
from tkinter import messagebox
import requests
import sqlite3
#peripercemi
# fetch stock price
def get_stock_price():
    symbol = symbol_entry.get().upper()
    api_key = 'KVXFJ2Y93UL7BJAR'
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval=5min&apikey={api_key}'

    try:
        response = requests.get(url)
        data = response.json()
        latest_data = data['Time Series (5min)']
        latest_timestamp = max(latest_data.keys())
        latest_price = float(latest_data[latest_timestamp]['1. open'])

        # دسترسی به database
        cursor.execute("SELECT price FROM stock_prices WHERE symbol=? ORDER BY timestamp DESC LIMIT 2", (symbol,))
        previous_prices = cursor.fetchall()

        if len(previous_prices) >= 2:
            previous_price = previous_prices[1][0]
            price_difference = latest_price - previous_price

            # the price has gone up or down مشخص کردن بالارفتن یا پایین امدن قیمت بورس
            if price_difference > 0:
                price_status = "Price has gone up."
                price_status_display.config(fg="green")
            elif price_difference < 0:
                price_status = "Price has gone down."
                price_status_display.config(fg="red")
            else:
                price_status = "Price remains unchanged."
                price_status_display.config(fg="blue")
        else:
            previous_price = 0
            price_status = "Not enough previous data available."
            price_status_display.config(fg="black")

        # Save data to database
        cursor.execute("INSERT INTO stock_prices (symbol, price) VALUES (?, ?)", (symbol, latest_price))
        conn.commit() 

        # Update labels
        result_label.config(text=f"The current price of {symbol} is ${latest_price:.2f}")
        previous_price_display.config(text=f"Previous Price: ${previous_price:.2f}")
        price_status_display.config(text=price_status)
    except Exception as e:
        messagebox.showerror("Error", f"Error fetching data for {symbol}: {e}")

# Connect to database
conn = sqlite3.connect('stock_prices.db')

# Create a table for storing data
cursor = conn.cursor()
cursor.execute('''
   CREATE TABLE IF NOT EXISTS stock_prices (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       symbol TEXT,
       price REAL,
       timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
   )
''')

# main window
window = tk.Tk()
window.title("Stock Price Tracker")
window.geometry("600x700")

symbol_label = tk.Label(window, text="Enter stock symbol:", font=20)
symbol_label.pack()

symbol_entry = tk.Entry(window)
symbol_entry.pack()

fetch_button = tk.Button(window, text="Fetch Price", command=get_stock_price)
fetch_button.pack()

price_frame = tk.LabelFrame(window, text="Prices", font=20)
price_frame.pack(padx=5, pady=10, fill="both", expand="yes")

result_label = tk.Label(price_frame, text="", font=20)
result_label.pack()

previous_price_display = tk.Label(price_frame, text="", font=20)
previous_price_display.pack()

price_status_display = tk.Label(price_frame, text="", fg="black", font=20)
price_status_display.pack()

intro_label = tk.Label(window, text="**You can write your specific symbol or choose from this table:**")
intro_label.pack()

symbols_label = tk.Label(window, text="", font=("Courier New", 12), justify=tk.LEFT)
symbols_label.pack()

pari_label = tk.Label(window, text="**PARVANEH PARCHAMI**")
pari_label.pack()

# suggest  some symbols
symbols_with_full_names = {
    "AAPL": "Apple Inc.",
    "MSFT": "Microsoft Corporation",
    "GOOGL": "Alphabet Inc.",
    "AMZN": "Amazon.com Inc.",
    "TSLA": "Tesla, Inc.",
    "GOOG": "Alphabet Inc. (Class C)",
    "FB": "Meta Platforms, Inc.",
    "NVDA": "NVIDIA Corporation",
    "JPM": "JPMorgan Chase & Co.",
    "V": "Visa Inc.",
    "PYPL": "PayPal Holdings, Inc.",
    "DIS": "The Walt Disney Company",
    "CRM": "Salesforce.com, Inc.",
    "INTC": "Intel Corporation",
    "NFLX": "Netflix, Inc.",
}

formatted_symbols = "\n".join([f"{symbol:<10} - {full_name}" for symbol, full_name in symbols_with_full_names.items()])
symbols_label.config(text=formatted_symbols)

window.mainloop()
conn.close()
