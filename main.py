import tkinter as tk
import customtkinter
import requests
import matplotlib.pyplot as plt
import matplotlib.style as mplstyle
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors as mpc
import yfinance as yf
from CTkScrollableDropdown import *
import os
from dotenv import load_dotenv

load_dotenv() 

use_api = False

#App setup
customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")
customtkinter.set_window_scaling(1)
customtkinter.set_widget_scaling(1)

#Main App
app = customtkinter.CTk()
app.title("Currency Exchange")
app.geometry('720x400')

#Charts app
#Chart window creation
charts = customtkinter.CTk()
charts.title("Charts")
charts.geometry('1000x500')

#Grid setup
app.columnconfigure((0,1,2,3), weight = 1)
app.rowconfigure((0,1,2,3,4), weight= 1)
col_count, row_count = app.grid_size()

title = customtkinter.CTkLabel(app, text="Currency Exchange", font = customtkinter.CTkFont(family = "Helvectia", size = 24, weight= "bold"))
title.grid(row = 0, column = 2, sticky = 'nw')

def show_error_message(message):
    # Create a new top-level window
    top_level = customtkinter.CTkToplevel()
    top_level.title("Error")

    # Place a label with the error message
    error_label = customtkinter.CTkLabel(top_level, text=message, font=customtkinter.CTkFont(size=14))
    error_label.pack(pady=20)

    # Add a button to close the window
    close_button = customtkinter.CTkButton(top_level, text="OK", command=top_level.destroy)
    close_button.pack(pady=10)

    # Center the window
    top_level.geometry("300x150")

#Calculates the exchange rate through the API
def exchange_rate(amount, base_currency, target_currency):
    api_key = os.getenv("API_KEY")
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/{base_currency}"

        
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for non-200 status codes

        # Parse the JSON response
        data = response.json()
    
        if target_currency in data["conversion_rates"]:
            result = float(amount) *data["conversion_rates"][target_currency]
            result = round(result, 3)
            result_label = customtkinter.CTkLabel(app, text= f"{amount} {base_currency} is equal to {result} {target_currency}", font = customtkinter.CTkFont(family= "Helvectia", weight= "bold", size= 18))
            result_label.place(x = 75,  y = 200, anchor= "nw")
        else:
            print(f"Error: Target currency '{target_currency}' not found in API response.")
            return None
    
    except requests.exceptions.RequestException as e:
        print(f"Error fetching exchange rate: {e}")
        return None
        
#Converts the currency
def convert_button_clicked():
    money = amount.get()
    base = from_currency.get()
    target = to_currency.get()
    
    if money == "0" or money == "":
        show_error_message("Please add a valid amount")
        return
    elif base == " ":
        show_error_message("Please add a valid base")
        return
    elif target == " ":
        show_error_message("Please add a valid target")
        return
    else:
        exchange_rate(money, base, target)
       
#Makes sure nothing except numbers and one decimal can be typed in the text field
def validate_amount(char, index, value):
    if char == ".":
        # Check if there's already a decimal point before the current index
        try:
            return "." not in value[:int(index)]
        except ValueError:
            # Handle non-integer index gracefully (e.g., prevent further decimals)
            return False
    return char.isdigit() or char == "."

def switch_to_charts():
    
    app.withdraw()

    window_title = customtkinter.CTkLabel(charts, text="Currency chart", font = customtkinter.CTkFont(family = "Helvectia", size = 24, weight= "bold"))
    window_title.grid(row=0, column = 1, sticky= 'nw', padx= 400)
    
    from_currency_label = customtkinter.CTkLabel(charts, text="From", font=customtkinter.CTkFont(family="Helvectia", weight="bold"))
    from_currency_label.grid(row=1, column=1, sticky='nw', padx=100)

    from_currency = customtkinter.CTkComboBox(charts, width=150, height=35)
    from_currency.set("USD")
    from_currency.grid(row=1, column=1, sticky='nw', padx=100, pady=30)

    CTkScrollableDropdown(from_currency, values=currency, justify="left")

    to_currency_label = customtkinter.CTkLabel(charts, text="To", font=customtkinter.CTkFont(family="Helvectia", weight="bold"))
    to_currency_label.grid(row=1, column=1, sticky='nw', padx=400)

    to_currency = customtkinter.CTkComboBox(charts, values=currency, width=150, height=35)
    to_currency.set("EUR")
    to_currency.grid(row=1, column=1, sticky='nw', pady=30, padx=400)

    CTkScrollableDropdown(to_currency, values=currency, justify="left")

    timeframe_options = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']

    timeframe_label= customtkinter.CTkLabel(charts, text="Timeframe", font=customtkinter.CTkFont(family="Helvectia", weight="bold"))
    timeframe_label.grid(row=1, column =1, sticky= 'nw', padx= 680)

    timeframe_selection = customtkinter.CTkComboBox(charts, values= timeframe_options,  width=150, height=35)
    timeframe_selection.set("1y")
    timeframe_selection.grid(row = 1, column= 1, pady= 30, padx= 680)

    CTkScrollableDropdown(timeframe_selection, values=timeframe_options, justify="left")

    create_graph_button = customtkinter.CTkButton(charts, text= "Create Graph", font = customtkinter.CTkFont(family = "Helvectia", weight= "bold"), fg_color= "transparent", border_width=2, border_color= None, text_color= None, command = lambda: create_graph(from_currency.get(), to_currency.get(), timeframe_selection.get()))
    create_graph_button.grid(row = 3, column = 1, sticky= 'nw', padx= 400)


    charts.mainloop()
    

def create_graph(base, target, timeframe):

    #Extracting information for yfinance
    currency_pair = f"{base}{target}=X"
    
    try:
        data = yf.download(currency_pair, period= timeframe)
        closing_prices = data["Close"]
        opening_prices = data["Open"]
        percent_change = ((closing_prices - opening_prices) / opening_prices) * 100
        overall_change = percent_change.iloc[-1]
    except Exception as e:
        error_label = customtkinter.CTkLabel(charts, text=f"Error downloading data: {e}", text_color="red")
        error_label.pack(pady=20)
        charts.mainloop()
        return
    
    

    #Graph set up
    plt.style.use('dark_background')
    fig = plt.figure(figsize= (10,3), dpi = 100, facecolor= '#242424')
    ax = fig.add_subplot(111)
    ax.set_facecolor("#242424")
    fig.tight_layout()
    #Determine if the color of the graph should be red or green based on its overall change
    if overall_change > 0:
        ax.plot(closing_prices, color = "green")
    else:
        ax.plot(closing_prices, color = "red")

    chart_frame = customtkinter.CTkFrame(charts)
    chart_frame.grid(row=3, column=1, sticky="nw", pady=80)
    chart_frame.grid_columnconfigure(0, weight=1)
    chart_frame.grid_rowconfigure(0, weight=1)
    mpc.cursor(hover = True)
    canvas = FigureCanvasTkAgg(fig, master=chart_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=customtkinter.BOTH, expand=True)
    

#Widget Creation

amount = customtkinter.CTkEntry(app, width= 200, height= 35, validate="key", validatecommand=(app.register(validate_amount), '%S', '%i','%P'))
amount.grid(row = 1, column = 1, sticky = 'nw', pady=30)

amount_label = customtkinter.CTkLabel(app, text = "Amount", font = customtkinter.CTkFont(family= "Helvectia", weight= "bold"))
amount_label.grid(row = 1, column = 1, sticky = 'nw')

currency = [
    "USD", "AED", "AFN", "ALL", "AMD", "ANG", "AOA", "ARS", "AUD", "AWG", 
    "AZN", "BAM", "BBD", "BDT", "BGN", "BHD", "BIF", "BMD", "BND", "BOB", 
    "BRL", "BSD", "BTN", "BWP", "BYN", "BZD", "CAD", "CDF", "CHF", "CLP", 
    "CNY", "COP", "CRC", "CUP", "CVE", "CZK", "DJF", "DKK", "DOP", "DZD", 
    "EGP", "ERN", "ETB", "EUR", "FJD", "FKP", "FOK", "GBP", "GEL", "GGP", 
    "GHS", "GIP", "GMD", "GNF", "GTQ", "GYD", "HKD", "HNL", "HRK", "HTG", 
    "HUF", "IDR", "ILS", "IMP", "INR", "IQD", "IRR", "ISK", "JEP", "JMD", 
    "JOD", "JPY", "KES", "KGS", "KHR", "KID", "KMF", "KRW", "KWD", "KYD", 
    "KZT", "LAK", "LBP", "LKR", "LRD", "LSL", "LYD", "MAD", "MDL", "MGA", 
    "MKD", "MMK", "MNT", "MOP", "MRU", "MUR", "MVR", "MWK", "MXN", "MYR", 
    "MZN", "NAD", "NGN", "NIO", "NOK", "NPR", "NZD", "OMR", "PAB", "PEN", 
    "PGK", "PHP", "PKR", "PLN", "PYG", "QAR", "RON", "RSD", "RUB", "RWF", 
    "SAR", "SBD", "SCR", "SDG", "SEK", "SGD", "SHP", "SLE", "SLL", "SOS", 
    "SRD", "SSP", "STN", "SYP", "SZL", "THB", "TJS", "TMT", "TND", "TOP", 
    "TRY", "TTD", "TVD", "TWD", "TZS", "UAH", "UGX", "UYU", "UZS", "VES", 
    "VND", "VUV", "WST", "XAF", "XCD", "XDR", "XOF", "XPF", "YER", "ZAR", 
    "ZMW", "ZWL"
]

from_currency = customtkinter.CTkComboBox(app, width= 150, height= 35)
from_currency.set("USD")
from_currency.grid(row = 1, column = 2, sticky = 'nw', padx=30, pady=30)

CTkScrollableDropdown(from_currency, values= currency, justify= "left")

from_currency_label = customtkinter.CTkLabel(app, text = "From", font = customtkinter.CTkFont(family = "Helvectia", weight= "bold"))
from_currency_label.grid(row = 1, column = 2, sticky = 'nw', padx= 30)

to_currency = customtkinter.CTkComboBox(app, values= currency, width= 150, height= 35)
to_currency.set("EUR")
to_currency.grid(row = 1, column = 3, sticky = 'nw', pady = 30)

CTkScrollableDropdown(to_currency, values= currency, justify= "left")

to_currency_label = customtkinter.CTkLabel(app, text = "To", font = customtkinter.CTkFont(family = "Helvectia", weight= "bold"))
to_currency_label.grid(row = 1, column = 3, sticky = 'nw')

convert_button = customtkinter.CTkButton(app, text = "Convert", font = customtkinter.CTkFont(family = "Helvectia", weight= "bold"), command= lambda: convert_button_clicked())
convert_button.grid(row = 3, column = 2, sticky = 'nswe', padx=40, pady=80)

view_charts_button = customtkinter.CTkButton(app, text = "View Charts",  font = customtkinter.CTkFont(family = "Helvectia", weight= "bold"), fg_color= "transparent", border_width=2, border_color= None, text_color= None, command = lambda: switch_to_charts())
view_charts_button.grid(row = 4, column = 2, sticky = 'nswe', padx=40)

app.mainloop()