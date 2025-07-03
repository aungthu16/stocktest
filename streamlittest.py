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

st.set_page_config(layout='wide')

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow:wght@400;500;600;700&display=swap');
    * {
        font-family: 'Barlow', sans-serif !important;
    }
    .streamlit-expanderContent {
        font-family: 'Barlow', sans-serif !important;
    }
    .stMarkdown {
        font-family: 'Barlow', sans-serif !important;
    }
    p {
        font-family: 'Barlow', sans-serif !important;
    }
    div {
        font-family: 'Barlow', sans-serif !important;
    }
    .stDataFrame {
        font-family: 'Barlow', sans-serif !important;
    }
</style>
""", unsafe_allow_html=True)

ticker = "aapl"
upper_ticker = ticker.upper()
exchange_value = "NASDAQ"

url = "https://stockanalysis.com/stocks/mcd/financials/balance-sheet/"
headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    
    if tables:
        for i, table in enumerate(tables):
            try:
                df = pd.read_html(str(table))[0]  # Convert to DataFrame
                st.write(f"### Table {i + 1}")
                st.dataframe(df)
            except Exception as e:
                st.warning(f"Could not parse Table {i + 1}: {e}")
    else:
        st.warning("No <table> elements found in the static HTML.")
else:
    st.error(f"Failed to fetch page. Status code: {response.status_code}")
