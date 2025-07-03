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

# url = "https://www.wallstreetzen.com/stocks/us/nyse/unh/ownership"
# headers = {
#     "User-Agent": "Mozilla/5.0"
# }
# response = requests.get(url, headers=headers)
# if response.status_code == 200:
#     soup = BeautifulSoup(response.text, "html.parser")
#     tables = soup.find_all("table")
    
#     if tables:
#         for i, table in enumerate(tables):
#             try:
#                 df = pd.read_html(str(table))[0]  # Convert to DataFrame
#                 st.write(f"### Table {i + 1}")
#                 st.dataframe(df)
#             except Exception as e:
#                 st.warning(f"Could not parse Table {i + 1}: {e}")
#     else:
#         st.warning("No <table> elements found in the static HTML.")
# else:
#     st.error(f"Failed to fetch page. Status code: {response.status_code}")

url = "https://www.wallstreetzen.com/stocks/us/nyse/med/revenue"
# headers = {
#     "User-Agent": "Mozilla/5.0"
# }

# response = requests.get(url, headers=headers)

# if response.status_code == 200:
#     soup = BeautifulSoup(response.text, "html.parser")
#     tables = soup.find_all("table")
    
#     if tables:
#         for i, table in enumerate(tables):
#             try:
#                 df = pd.read_html(str(table))[0]  # Convert to DataFrame
#                 st.write(f"### Table {i + 1}")
#                 st.dataframe(df)
#             except Exception as e:
#                 st.warning(f"Could not parse Table {i + 1}: {e}")
#     else:
#         st.warning("No <table> elements found in the static HTML.")
# else:
#     st.error(f"Failed to fetch page. Status code: {response.status_code}")


# url = f'https://www.wallstreetzen.com/stocks/us/nyse/med/revenue'
# headers = {"User-Agent": "Mozilla/5.0"}
# response = requests.get(url, headers=headers)
# if response.status_code == 200:
#     soup = BeautifulSoup(response.text, "html.parser")
#     tables = soup.find_all("table")
#     if len(tables) >= 0:
#         try:
#             zen_rev = pd.read_html(str(tables[0]))[0]
#         except Exception as e:
#             zen_rev = ""
#     else:
#         zen_rev = ""
# else:
#     zen_rev = ""

url = f'https://www.wallstreetzen.com/stocks/us/nyse/med/revenue'
response = requests.get(url)
if response.status_code == 200:
    soup = BeautifulSoup(response.text, "html.parser")
    tables = soup.find_all("table")
    if len(tables) >= 0:
        try:
            zen_rev = pd.read_html(str(tables[0]))[0]
        except Exception as e:
            zen_rev = ""
    else:
        zen_rev = ""
else:
    zen_rev = ""

st.write(zen_rev)
zen_rev_df = pd.DataFrame(zen_rev)
zen_df_plot = zen_rev_df.iloc[:, [0, 1]].copy()
zen_df_plot.columns = ['Date', 'Revenue']
zen_df_plot['Date'] = pd.to_datetime(zen_df_plot['Date'])
def zen_convert_to_number(value):
    if value in ("-", None):
        return 0
    value = value.replace("$", "").strip()
    if value.endswith("B"):
        return float(value[:-1]) * 1e9
    elif value.endswith("M"):
        return float(value[:-1]) * 1e6
    else:
        return float(value)
zen_df_plot["Revenue"] = zen_df_plot["Revenue"].apply(zen_convert_to_number)
zen_df_plot = zen_df_plot.sort_values('Date')
fig = go.Figure()
fig.add_trace(
    go.Bar(
        x=zen_df_plot['Date'].dt.year,
        y=zen_df_plot['Revenue'],
        name="Revenue",
        marker=dict(color="#4FC1E9") 
    )
)
fig.update_layout(
    title={"text": "Revenue History", "font": {"size": 22}},
    title_y=1,
    title_x=0.75,
    margin=dict(t=30, b=40, l=10, r=20),
    xaxis_title=None,
    yaxis_title="Revenue (USD)",
    xaxis=dict(type="category"),
    height=400,
)
st.plotly_chart(fig, use_container_width=True)
