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

ticker = "AAPL"

try:
        url = f'https://stockanalysis.com/stocks/{ticker}/forecast/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text,"lxml")
        table = soup.find("table",class_ = "w-full whitespace-nowrap border border-gray-200 text-right text-sm dark:border-dark-700 sm:text-base")
        rows = table.find_all("tr")
        headers = []
        data = []
        for row in rows:
            cols = row.find_all(["th", "td"])
            cols_text = [col.text.strip() for col in cols]
            if not headers:
                headers = cols_text
            else:
                data.append(cols_text)
        sa_growth_df = pd.DataFrame(data, columns=headers)
        sa_growth_df = sa_growth_df.iloc[1:, :-1].reset_index(drop=True)
except Exception as e: 
        sa_growth_df = ""
        st.write(e)

st.write(sa_growth_df)

try:
        if not isinstance(sa_growth_df, str) and not sa_growth_df.empty:
            growth_metrics = ['Revenue Growth', 'EPS Growth']
            sa_growth_df_filtered = sa_growth_df[sa_growth_df['Fiscal Year'].isin(growth_metrics)]
            sa_growth_metrics_df_melted = sa_growth_df_filtered.melt(id_vars=['Fiscal Year'], var_name='Year', value_name='Value')
            growth_unique_years = sa_growth_metrics_df_melted['Year'].unique()
            growth_unique_years_sorted = sorted([year for year in growth_unique_years if year != 'Current'])
            if 'Current' in growth_unique_years:
                growth_unique_years_sorted.append('Current')
            fig_growth = go.Figure()
            for fiscal_year in sa_growth_metrics_df_melted['Fiscal Year'].unique():
                filtered_data = sa_growth_metrics_df_melted[sa_growth_metrics_df_melted['Fiscal Year'] == fiscal_year]
                fig_growth.add_trace(go.Scatter(
                    x=filtered_data['Year'],
                    y=filtered_data['Value'],
                    mode='lines+markers',
                    name=str(fiscal_year)
                ))
            fig_growth.update_layout(
                title={"text":"Growth Data", "font": {"size": 20}},
                title_y=1,  
                title_x=0, 
                margin=dict(t=30, b=30, l=40, r=30),
                xaxis_title=None,
                yaxis_title='Value (%)',
                xaxis=dict(tickmode='array', tickvals=growth_unique_years_sorted,showgrid=True),
                yaxis=dict(showgrid=True),
                legend=dict(yanchor="top",y=0.99,xanchor="left",x=0.010),
                height=400
            )
            st.plotly_chart(fig_growth, use_container_width=True)
except Exception as e:
            st.warning(f'{ticker} has no growth estimates data.')
