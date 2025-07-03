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

mb_com_url = f'https://www.macrotrends.net/stocks/charts/MED/medifast-inc/revenue'
headers_request = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"}
mb_com_response = requests.get(mb_com_url, headers=headers_request)
if mb_com_response.status_code == 200:
    try:
        tables_dfs = pd.read_html(mb_com_response.text)
        if len(tables_dfs) > 1:
            mb_com_df = tables_dfs[0]
            st.write("DataFrame created successfully using pd.read_html():")
            st.write(mb_com_df)
        else:
            st.error("Could not find the second table on the MarketBeat page.")
            mb_com_df = pd.DataFrame() 
    except Exception as e:
        st.error(f"Error parsing tables with pd.read_html: {e}")
        mb_com_df = pd.DataFrame() 
else:
    st.error(f"Failed to fetch page from MarketBeat. Status code: {mb_com_response.status_code}")
    mb_com_df = pd.DataFrame() 
