import streamlit as st
from streamlit_extras.add_vertical_space import add_vertical_space
import streamlit.components.v1 as components
import matplotlib.pyplot as plt
from helpers import *
import os, time, random, datetime, re, pickle, time, psutil
import yfinance as yf
import pandas as pd

tickers = ["NVDA", "MSFT", "GOOGL", "BTC", "ETH"]
#tickers = ["NVDA"]

start_date = "2023-12-12"
end_date = pd.Timestamp.today().strftime('%Y-%m-%d')  # Heute

# Ergebnisse für alle Ticker
results = {}
historical_data = []

# Für jeden Ticker
for ticker_symbol in tickers:
    print(f"Verarbeitung für: {ticker_symbol}")
    
    # Historische Daten abrufen
    ticker = yf.Ticker(ticker_symbol)
    historical_data.append(ticker.history(start=start_date, end=end_date, interval="1d"))
#    print(historical_data)
    
    # Nur die Schlusskurse verwenden
    close_prices = historical_data[-1]['Close']
    
    # Fehlende Kurse mit dem letzten bekannten Kurs auffüllen (Forward Fill)
    close_prices = close_prices.ffill()

    # Intervallpaare generieren
    intervals = []
    current_start = pd.Timestamp(start_date)
    while current_start + pd.DateOffset(years=2) <= pd.Timestamp(end_date):
        current_end = current_start + pd.DateOffset(years=2)
        intervals.append((current_start, current_end))
        current_start += pd.DateOffset(months=3)  # Verschiebung um 3 Monate
    
    # Berechnung der prozentualen Veränderung
    changes = []
    close_prices.index = close_prices.index.tz_localize(None)

    # Konvertiere start und end ebenfalls zu tz-naive
    for start, end in intervals:
        start = start.tz_localize(None)
        end = end.tz_localize(None)

        # Überprüfen, ob die Start- und Enddaten in den Daten vorhanden sind
        if start in close_prices.index and end in close_prices.index:
            start_price = close_prices.loc[start]
            end_price = close_prices.loc[end]
            change = ((end_price - start_price) / start_price) * 100
            changes.append((start, end, change))
        else:
            if start not in close_prices.index:
                start_price = close_prices.asof(start)
            else:
                start_price = close_prices.loc[start]

            if end not in close_prices.index:
                end_price = close_prices.asof(end)
            else:
                end_price = close_prices.loc[end]

            if start_price is not None and end_price is not None:
                change = ((end_price - start_price) / start_price) * 100
                changes.append((start, end, change))
    
    # Analyse der Ergebnisse
    if changes:
        best_interval = max(changes, key=lambda x: x[2])  # Höchste Veränderung
        worst_interval = min(changes, key=lambda x: x[2])  # Niedrigste Veränderung
        average_change = sum([x[2] for x in changes]) / len(changes)  # Durchschnitt
        
        # Speichern der Ergebnisse
        results[ticker_symbol] = {
            "Best": best_interval,
            "Worst": worst_interval,
            "Average": average_change
        }
    else:
        results[ticker_symbol] = {
            "Best": None,
            "Worst": None,
            "Average": None
        }


##    for ticker, result in results.items():
##        print(f"\nErgebnisse für {ticker}:")
##        if result["Best"] and result["Worst"]:
##            print(f"  Beste Veränderung: {result['Best'][2]:.2f}% ({result['Best'][0]} bis {result['Best'][1]})")
##            print(f"  Schlechteste Veränderung: {result['Worst'][2]:.2f}% ({result['Worst'][0]} bis {result['Worst'][1]})")
##            print(f"  Durchschnittliche Veränderung: {result['Average']:.2f}%")
##        else:
##            print("  Keine ausreichenden Daten für Berechnungen.")
        
        
def combine(l):
    new_list = []
    for item in l:
        if item==0:
            new_list += pulse(TD, VLO, VHI)
        elif item==1:
            new_list += pulse(TD, VHI, VLO)
        else:
            new_list += func_delay()
    return new_list

# CSS für weniger Abstand nach oben
##st.markdown("""
##    <style>
##    .css-1d391kg {  /* Haupt-Container */
##        padding-top: 0rem;
##    }
##    .css-1d391kg > div:nth-child(1) {  /* Sidebar spezifisch */
##        padding-top: -1rem;
##    }
##    </style>
##    """, unsafe_allow_html=True)

# App title
st.set_page_config(page_title="Chart", layout="wide")

st.markdown("""
    <style>
    /* Entferne Standard-Padding und Abstand der Sidebar */
    [data-testid="stSidebar"] {
        padding-top: 0rem;
        padding-bottom: 0rem;
    }
    /* Entferne Abstand oben von Hauptcontainer */
    .css-1d391kg {  
        padding-top: 0rem;
    }
    </style>
    """, unsafe_allow_html=True)

if 'text' not in st.session_state:
    st.session_state.text = ""

def random_color():
    return [random.random() for _ in range(3)]  # RGB-Werte zwischen 0 und 1

def generate():
    # calculate and redraw diagram
    
    plot_piecewise_function()

    ##    print('Hallo')
##    st.session_state.text = 'Abcdef'
    # 12 Zeilen mit 4 Hexadezimalzahlen pro Zeile
    hex_table = [
        "\t".join(f"{random.randint(0, 255):02X}" for _ in range(4))
        for _ in range(3)
    ]
    # Verbinden der Zeilen mit Zeilenumbrüchen
    st.session_state.text = "\n".join(hex_table)

plot_placeholder = st.empty()

# Funktion zum Plotten einer piecewise linearen Funktion
def plot_piecewise_function():
    fig, ax = plt.subplots(figsize=(6, 3.1))
#    ax.plot(x_values, y_values, marker="", linestyle="-", color="b")
    i = 0
    for ticker_symbol in tickers:
        ax.plot(historical_data[i].index, historical_data[i]['Close']/ historical_data[i]['Close'][0], label=ticker_symbol, color=random_color())
        i += 1
        
    ax.set_title("Time", fontsize=8)
    ax.set_xlabel("Date", fontsize=6)
    ax.set_ylabel("US $", fontsize=6)
    ax.tick_params(axis='x', labelsize=4)
    ax.tick_params(axis='y', labelsize=6)
#    ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)
    
# Sidebar
with st.sidebar:
    st.title("Chart viewer")    
    st.image('static/chart_icon.png', width=240)

st.sidebar.button('Generate', on_click=generate)

exit_app = st.sidebar.button("Exit App")
if exit_app:
    time.sleep(.3); pid = os.getpid(); p = psutil.Process(pid);  p.terminate();

days = st.sidebar.number_input("days", min_value=0, max_value=10000, value=365, step=1)
##threshold = st.sidebar.slider('threshold', min_value=0.5, max_value=25.0, value=2.0, step=0.1)
##adj = st.sidebar.slider('temp adjust', min_value=-7, max_value=8, value=0, step=1)

st.image('static/bot3.png', width=64)
txt = '<div class="chat-row">'
#    div += '<img class="chat-icon" src="./app/static/ai_icon1.png" width=40 height=40>'
txt += '<div class="chat-bubble ai-bubble">'+'Hello, please make your inputs and generate.\n'+' </div>  </div>'
    
st.markdown(txt, unsafe_allow_html=True)
add_vertical_space(1)
st.text_area('Results:', value=st.session_state.text, height=170)

# Beispielwerte für die piecewise lineare Funktion
x_values = [0, 100]
y_values = [0, 0]

if "initialized" not in st.session_state:
    # Plot der Funktion über der Textbox
    plot_piecewise_function()
    st.session_state.initialized = False


