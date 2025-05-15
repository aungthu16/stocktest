import streamlit as st
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import math
import numpy as np
import http.client
import json
import pandas as pd
import plotly.graph_objects as go
import datetime
import re
from dateutil.relativedelta import relativedelta
import pytz
from groq import Groq

upper_ticker = "AAPL"
exchange_value = "NASDAQ"

try:
    insider_mb_url = f'https://www.marketbeat.com/stocks/{exchange_value}/{upper_ticker}/insider-trades/'
    response = requests.get(insider_mb_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    tables = soup.find_all('table')
    if len(tables) >= 0:
        try:
            insider_mb = pd.read_html(str(tables[0]))[0]
            if insider_mb.empty:
                insider_mb = pd.DataFrame()
        except Exception as e:
            st.warning(f"Failed to parse table: {e}")
            insider_mb = pd.DataFrame()
    else:    
        insider_mb = ""
except: insider_mb = ""

st.write(insider_mb)

def highlight_insider_trades(val):
    if val == 'Buy':
        bscolor = 'green'
    elif val == 'Sell':
        bscolor = 'red'
    else:
        bscolor ='#AAB2BD'
    return f'background-color: {bscolor}; color: white'

try:
    if not insider_mb.empty:  
        insider_mb = insider_mb.iloc[:, :-2]
        def is_valid_date(value):
            try:
                pd.to_datetime(value)
                return True
            except ValueError:
                return False
        unwanted_string = "Get Insider Trades Delivered To Your InboxEnter your email address below to receive a concise daily summary of insider buying activity, insider selling activity and changes in hedge fund holdings."
        filtered_insider_mb = insider_mb[
            insider_mb["Transaction Date"].apply(lambda x: is_valid_date(x) and x != unwanted_string)
        ]
        st.dataframe(filtered_insider_mb.style.applymap(highlight_insider_trades, subset=['Buy/Sell']), use_container_width=True, hide_index=True, height = 600)
        st.caption("Data source: Market Beat")
    else:
        st.warning("Insider information is not available.")
except Exception as e:
    st.warning("Insider information is not available.")
    st.write(e)
