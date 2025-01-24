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

st.set_page_config(page_title='US Stock Analysis Tool', layout='wide', page_icon="./Image/logo.png")

@st.cache_data(ttl=3600)
def get_stock_data(ticker):

    stock = yf.Ticker(ticker)
    lowercase_ticker = ticker.lower()
    upper_ticker = ticker.upper()
    price = stock.info.get('currentPrice', 'N/A')
    picture_url = f'https://logos.stockanalysis.com/{lowercase_ticker}.svg'
    exchange = stock.info.get('exchange', 'N/A')
    if exchange == 'NYQ':
        exchange_value = "NYSE"
    elif exchange == 'NMS':
        exchange_value = "NASDAQ"
    else:
        exchange_value = "N/A"
    lower_exchange = exchange_value.lower()
    
    try:
        end_date = datetime.today()
        start_date = (end_date - datetime.timedelta(days=int(2 * 365)))
        start_date_1y = (end_date - datetime.timedelta(days=int(1 * 365)))
        extended_data_r = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1d")
        extended_data_r.columns = extended_data_r.columns.map('_'.join)
        extended_data_r.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
        macd_data_r = yf.download(ticker, start=start_date_1y.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1d")
        macd_data_r.columns = macd_data_r.columns.map('_'.join)
        macd_data_r.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
        rsi_data_r = yf.download(ticker, start=start_date_1y.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1d")
        rsi_data_r.columns = rsi_data_r.columns.map('_'.join)
        rsi_data_r.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
        ta_data_r = yf.download(ticker, start=start_date_1y.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1d")
        ta_data_r.columns = ta_data_r.columns.map('_'.join)
        ta_data_r.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
    except: end_date = extended_data_r = macd_data_r = rsi_data_r = ta_data_r = ""

    try:
        eps_yield = eps/price
    except: eps_yield = "N/A"
    
    return end_date , extended_data_r , macd_data_r , rsi_data_r , ta_data_r , ticker

''
''
#############################################        #############################################
############################################# Inputs #############################################
#############################################        #############################################

main_col1, main_col2 = st.columns([3,1])
with main_col1:
    st.title("US Stock Analysis Tool")
    input_col1, input_col2, input_col3 = st.columns([1, 3, 1])
    with input_col1:
        ticker = st.text_input("Enter US Stock Ticker:", "AAPL")
    with input_col2:
        apiKey = st.text_input("Enter your RapidAPI Key (optional):", "")

st.write("This analysis dashboard is designed to enable beginner investors to analyze stocks effectively and with ease. Please note that the information in this page is intended for educational purposes only and it does not constitute investment advice or a recommendation to buy or sell any security. We are not responsible for any losses resulting from trading decisions based on this information.")
st.info('Data is sourced from Yahoo Finance, Morningstar, Seeking Alpha, Market Beat, Stockanalysis.com and Alpha Spread. Certain sections require API keys to operate. Users are advised to subscribe to the Morningstar and Seeking Alpha APIs provided by Api Dojo through rapidapi.com.')

if st.button("Get Data"):
    try:
            end_date , extended_data_r , macd_data_r , rsi_data_r , ta_data_r , ticker = get_stock_data(ticker)
     


#############################################                         #############################################
############################################# Technical Analysis Data #############################################
#############################################                         #############################################
            st.info("It is important to note that investment decisions should not be based solely on technical analysis. Technical analysis primarily relies on historical price movements and cannot predict future outcomes with certainty.")
            st.caption("This page is derived from the historical price data provided by Yahoo Finance.")
            try:
                extended_data = extended_data_r 
                macd_data = macd_data_r 
                rsi_data = rsi_data_r 
                ta_data = ta_data_r
                ta_data = ta_data[['High', 'Low', 'Close']].copy()
                if extended_data.empty:
                    st.error("No data available for the specified ticker. Please check the ticker symbol and try again.")
                else:
                    #SMA
                    extended_data['SMA20'] = extended_data['Close'].rolling(window=20).mean()
                    extended_data['SMA50'] = extended_data['Close'].rolling(window=50).mean()
                    extended_data['SMA200'] = extended_data['Close'].rolling(window=200).mean()
                    last_year_start = (end_date - datetime.timedelta(days=int(1 * 365))).replace(tzinfo=pytz.UTC)
                    data = extended_data.loc[extended_data.index >= last_year_start]
                    data.columns = data.columns.map('_'.join)
                    data.columns = ['Adj Close', 'Close', 'High', 'Low', 'Open', 'Volume', 'SMA20', 'SMA50', 'SMA200']
                    volume_colors = ['green' if data['Close'][i] >= data['Open'][i] else 'red' for i in range(len(data))]
                    max_volume = data['Volume'].max()
                    #MACD
                    macd_data['EMA12'] = macd_data['Close'].ewm(span=12, adjust=False).mean()
                    macd_data['EMA26'] = macd_data['Close'].ewm(span=26, adjust=False).mean()
                    macd_data['MACD'] = macd_data['EMA12'] - macd_data['EMA26']
                    macd_data['Signal'] = macd_data['MACD'].ewm(span=9, adjust=False).mean()
                    macd_data['MACD_Hist'] = macd_data['MACD'] - macd_data['Signal']
                    macd_data['Crossover'] = macd_data['MACD'] > macd_data['Signal']
                    macd_data['Bullish_Crossover'] = (macd_data['Crossover'] != macd_data['Crossover'].shift(1)) & (macd_data['Crossover'] == True)
                    macd_data['Bearish_Crossover'] = (macd_data['Crossover'] != macd_data['Crossover'].shift(1)) & (macd_data['Crossover'] == False)
                    macd_latest_bullish = macd_data['Bullish_Crossover'].iloc[-1]
                    macd_latest_bearish = macd_data['Bearish_Crossover'].iloc[-1]
                    #macd_data = macd_data[macd_data.index.dayofweek < 5]
                    #RSI
                    change = rsi_data["Close"].diff()
                    change.dropna(inplace=True)
                    up = change.apply(lambda x: max(x, 0))
                    down = change.apply(lambda x: -min(x, 0))
                    rsi_length = 14
                    avg_up = up.ewm(alpha=1/rsi_length, min_periods=rsi_length).mean()
                    avg_down = down.ewm(alpha=1/rsi_length, min_periods=rsi_length).mean()
                    rsi_data['RSI'] = 100 - (100 / (1 + avg_up / avg_down))
                    rsi_data['RSI'] = rsi_data['RSI'].apply(lambda x: 100 if avg_down.iloc[0] == 0 else (0 if avg_up.iloc[0] == 0 else x))
                    latest_rsi = rsi_data['RSI'].iloc[-1]
                    prev_rsi = rsi_data['RSI'].iloc[-2]
                    # Stochastic Oscillator (%K and %D)
                    ta_data['Low14'] = ta_data['Low'].rolling(window=14).min()
                    ta_data['High14'] = ta_data['High'].rolling(window=14).max()
                    ta_data['%K'] = 100 * ((ta_data['Close'] - ta_data['Low14']) / (ta_data['High14'] - ta_data['Low14']))
                    ta_data['%D'] = ta_data['%K'].rolling(window=3).mean()
                    ta_data['STOCH'] = ta_data['%D']
                    # Average Directional Index (ADX)
                    ta_data['+DM'] = np.where((ta_data['High'] - ta_data['High'].shift(1)) > (ta_data['Low'].shift(1) - ta_data['Low']), 
                                        ta_data['High'] - ta_data['High'].shift(1), 0)
                    ta_data['-DM'] = np.where((ta_data['Low'].shift(1) - ta_data['Low']) > (ta_data['High'] - ta_data['High'].shift(1)), 
                                        ta_data['Low'].shift(1) - ta_data['Low'], 0)
                    ta_data['TR'] = np.maximum(ta_data['High'] - ta_data['Low'], 
                                            np.maximum(abs(ta_data['High'] - ta_data['Close'].shift(1)), 
                                                    abs(ta_data['Low'] - ta_data['Close'].shift(1))))
                    ta_data['ATR'] = ta_data['TR'].rolling(window=14).mean()
                    ta_data['+DI'] = 100 * (ta_data['+DM'] / ta_data['ATR']).rolling(window=14).mean()
                    ta_data['-DI'] = 100 * (ta_data['-DM'] / ta_data['ATR']).rolling(window=14).mean()
                    ta_data['DX'] = 100 * abs((ta_data['+DI'] - ta_data['-DI']) / (ta_data['+DI'] + ta_data['-DI']))
                    ta_data['ADX'] = ta_data['DX'].rolling(window=14).mean()
                    # Williams %R
                    ta_data['Williams %R'] = ((ta_data['High14'] - ta_data['Close']) / (ta_data['High14'] - ta_data['Low14'])) * -100
                    # Commodity Channel Index (CCI)
                    ta_data['Mean Price'] = (ta_data['High'] + ta_data['Low'] + ta_data['Close']) / 3
                    ta_data['CCI'] = (ta_data['Mean Price'] - ta_data['Mean Price'].rolling(window=20).mean()) / (0.015 * ta_data['Mean Price'].rolling(window=20).std())
                    # Rate of Change (ROC)
                    ta_data['ROC'] = ((ta_data['Close'] - ta_data['Close'].shift(12)) / ta_data['Close'].shift(12)) * 100
                    # Ultimate Oscillator (UO)
                    ta_data['BP'] = ta_data['Close'] - np.minimum(ta_data['Low'], ta_data['Close'].shift(1))
                    ta_data['TR_UO'] = np.maximum(ta_data['High'] - ta_data['Low'], 
                                            np.maximum(abs(ta_data['High'] - ta_data['Close'].shift(1)), 
                                                        abs(ta_data['Low'] - ta_data['Close'].shift(1))))
                    ta_data['Avg7'] = ta_data['BP'].rolling(window=7).sum() / ta_data['TR_UO'].rolling(window=7).sum()
                    ta_data['Avg14'] = ta_data['BP'].rolling(window=14).sum() / ta_data['TR_UO'].rolling(window=14).sum()
                    ta_data['Avg28'] = ta_data['BP'].rolling(window=28).sum() / ta_data['TR_UO'].rolling(window=28).sum()
                    ta_data['UO'] = 100 * (4 * ta_data['Avg7'] + 2 * ta_data['Avg14'] + ta_data['Avg28']) / 7
                    #
                    fig = go.Figure()
                    fig_macd = go.Figure()
                    fig_rsi = go.Figure()
                    #
                    rsi_latest = rsi_data['RSI'].iloc[-1]
                    rsi_score = 80 if rsi_latest < 30 else 20 if rsi_latest > 70 else 50
                    macd_latest = macd_data['MACD'].iloc[-1]
                    signal_latest = macd_data['Signal'].iloc[-1]
                    macd_score = 80 if macd_latest > signal_latest else 20
                    ma_scores = []
                    if extended_data['Close'].iloc[-1] > extended_data['SMA20'].iloc[-1]: ma_scores.append(80)
                    else: ma_scores.append(20) 
                    if extended_data['Close'].iloc[-1] > extended_data['SMA50'].iloc[-1]: ma_scores.append(80)
                    else: ma_scores.append(20)
                    if extended_data['Close'].iloc[-1] > extended_data['SMA200'].iloc[-1]: ma_scores.append(80)
                    else: ma_scores.append(20)
                    ma_score = np.mean(ma_scores)
                    stoch_latest =  ta_data['STOCH'].iloc[-1]
                    stoch_score = 80 if stoch_latest > 80 else 20 if stoch_latest < 20 else 50
                    adx_latest = ta_data['ADX'].iloc[-1]
                    adx_score = 80 if adx_latest > 25 else 50
                    williamsr_latest = ta_data['Williams %R'].iloc[-1]
                    williamsr_score = 80 if williamsr_latest < -80 else 20 if williamsr_latest > -20 else 50
                    cci_latest = ta_data['CCI'].iloc[-1]
                    cci_score = 80 if cci_latest > 100 else 20 if cci_latest < -100 else 50
                    roc_latest = ta_data['ROC'].iloc[-1]
                    roc_score = 80 if roc_latest > 0 else 20
                    uo_latest = ta_data['UO'].iloc[-1]
                    uo_score = 80 if uo_latest > 70 else 20 if uo_latest < 30 else 50
                    overall_score = np.mean([rsi_score, macd_score, ma_score,stoch_score, adx_score, williamsr_score, cci_score, roc_score, uo_score])
                    #
                    def get_signal(price, sma, period):
                        if price > sma:
                            return f"🟢  {ticker}'s share price is ${price:.2f} and {period}SMA is {sma:.2f}, suggesting a BUY signal."
                        else:
                            return f"🔴  {ticker}'s share price is ${price:.2f} and {period}SMA is {sma:.2f}, suggesting a SELL signal."
                    def get_shortsignal(price, sma, period):
                        if price > sma:
                            return "Buy"
                        else:
                            return "Sell"
                    def detect_cross(data, short_sma, long_sma, short_period, long_period):
                        last_cross = None
                        if extended_data[short_sma].iloc[-2] < extended_data[long_sma].iloc[-2] and extended_data[short_sma].iloc[-1] > extended_data[long_sma].iloc[-1]:
                            last_cross = f"🟢  Golden Cross: {short_period}SMA crossed above the {long_period}SMA."
                        elif extended_data[short_sma].iloc[-2] > extended_data[long_sma].iloc[-2] and extended_data[short_sma].iloc[-1] < extended_data[long_sma].iloc[-1]:
                            last_cross = f"🔴  Death Cross: {short_period}SMA crossed below the {long_period}SMA."
                        return last_cross
                    cross_20_50 = detect_cross(data, 'SMA20', 'SMA50', 20, 50)
                    cross_50_200 = detect_cross(data, 'SMA50', 'SMA200', 50, 200)
                    def get_sentiment_label(score):
                        if score <= 20:
                            return "Strong Negative Bias"
                        elif score <= 40:
                            return "Negative Bias"
                        elif score <= 60:
                            return "Neutral"
                        elif score <= 80:
                            return "Positive Bias"
                        else:
                            return "Strong Positive Bias"
                    def consensus(value, thresholds):
                        if value < thresholds[0]:
                            return "Strong Sell"
                        elif value < thresholds[1]:
                            return "Sell"
                        elif value < thresholds[2]:
                            return "Neutral"
                        elif value < thresholds[3]:
                            return "Buy"
                        else:
                            return "Strong Buy"
                    def create_gauge(title, score):
                        label = get_sentiment_label(score)
                        fig = go.Figure(go.Indicator(
                            mode="gauge",
                            value=score,  
                            number={'font': {'size': 24}},  
                            title={'text': title, 'font': {'size': 20}},
                            gauge={'axis': {'range': [0, 100]},
                                'bar': {'color': "#5F9BEB"},
                                'steps': [
                                    {'range': [0, 15], 'color': "#da4453", 'name': 'Strong Neg'},
                                    {'range': [15, 45], 'color': "#e9573f", 'name': 'Neg'},
                                    {'range': [45, 55], 'color': "#f6bb42", 'name': 'Neutral'},
                                    {'range': [55, 85], 'color': "#a0d468", 'name': 'Pos'},
                                    {'range': [85, 100], 'color': "#37bc9b", 'name': 'Strong Pos'}]}))
                        fig.add_annotation(x=0.5, y=0.25, text=label, showarrow=False, font=dict(size=20))
                        fig.update_layout(
                            font=dict(size=14),
                            margin=dict(t=30, b=30, l=50, r=50),
                            )
                        return fig
                    #thresholds for table
                    ta_data['STOCH Consensus'] = ta_data['%K'].apply(lambda x: consensus(x, [20, 40, 60, 80]))
                    ta_data['ADX Consensus'] = ta_data['ADX'].apply(lambda x: "Strong Trend" if x > 25 else "Weak Trend")
                    ta_data['Williams %R Consensus'] = ta_data['Williams %R'].apply(lambda x: consensus(x, [-80, -50, -20, 0]))
                    ta_data['CCI Consensus'] = ta_data['CCI'].apply(lambda x: consensus(x, [-100, -50, 50, 100]))
                    ta_data['ROC Consensus'] = ta_data['ROC'].apply(lambda x: consensus(x, [-5, 0, 5, 10]))
                    ta_data['UO Consensus'] = ta_data['UO'].apply(lambda x: consensus(x, [30, 50, 70, 80]))
                    #
                    fig.add_trace(go.Candlestick(
                        x=data.index,
                        open=data['Open'], high=data['High'], low=data['Low'], close=data['Close'],
                        name="Candlestick",
                        showlegend=False,
                        increasing_line_width=0.5, decreasing_line_width=0.5,
                        opacity=1
                    ))
                    fig.add_trace(go.Scatter(
                        x=data.index, y=data['SMA20'],
                        line=dict(color='#3BAFDA', width=1),
                        name="SMA 20",
                        opacity=0.5
                    ))
                    fig.add_trace(go.Scatter(
                        x=data.index, y=data['SMA50'],
                        line=dict(color='#F6BB42', width=1),
                        name="SMA 50",
                        opacity=0.5
                    ))
                    fig.add_trace(go.Scatter(
                        x=data.index, y=data['SMA200'],
                        line=dict(color='#D772AD', width=1.5),
                        name="SMA 200",
                        opacity=0.5
                    ))
                    fig.add_trace(go.Bar(
                        x=data.index, y=data['Volume'],
                        marker=dict(color=volume_colors),
                        name="Volume",
                        yaxis="y2",
                        showlegend=False,  
                        opacity=0.3  
                    ))
                    tick_vals = data.index[::30]
                    tick_text = [date.strftime("%b %Y") for date in tick_vals]
                    fig.update_layout(
                        title={"text":f"Moving Average and Price Data", "font": {"size": 30}},
                        xaxis_rangeslider_visible=False,
                        xaxis=dict(
                            type="category",
                            showgrid=True,
                            ticktext=tick_text,
                            tickvals=tick_vals
                        ),
                        yaxis=dict(
                            title="Price (USD)",
                            side="left",
                            showgrid=True
                        ),
                        yaxis2=dict(
                            side="right",
                            overlaying="y",
                            showgrid=False,
                            range=[0, max_volume * 3],
                            showticklabels=False
                        )
                    )
                    fig_macd.add_trace(go.Scatter(
                        x=macd_data.index, y=macd_data['MACD'],
                        line=dict(color='#3BAFDA', width=1.5),
                        opacity=0.5,
                        name="MACD"
                    ))
                    fig_macd.add_trace(go.Scatter(
                        x=macd_data.index, y=macd_data['Signal'],
                        line=dict(color='#F6BB42', width=1),
                        opacity=1,
                        name="Signal"
                    ))
                    fig_macd.add_trace(go.Bar(
                        x=macd_data.index, y=macd_data['MACD_Hist'].where(macd_data['MACD_Hist'] >= 0, 0),  
                        marker=dict(color='green'),
                        showlegend=False,
                        opacity=0.5,
                        name="MACD Histogram (Above Zero)"
                    ))
                    fig_macd.add_trace(go.Bar(
                        x=macd_data.index, y=macd_data['MACD_Hist'].where(macd_data['MACD_Hist'] < 0, 0),  
                        marker=dict(color='red'),
                        showlegend=False,
                        opacity=0.5,
                        name="MACD Histogram (Below Zero)"
                    ))
                    tick_vals = macd_data.index[::30]
                    tick_text = [date.strftime("%b %Y") for date in tick_vals]
                    fig_macd.update_layout(
                        title={"text":f"MACD Chart", "font": {"size": 30}}, xaxis_title="Date", yaxis_title="MACD Value",
                        xaxis_rangeslider_visible=False,
                        xaxis=dict(
                            type="category",
                            ticktext=tick_text,
                            tickvals=tick_vals,
                            showgrid=True
                        )
                    )
                    fig_rsi.add_trace(go.Scatter(
                        x=rsi_data.index, y=rsi_data['RSI'],
                        line=dict(color='#D772AD', width=1),
                        name="RSI"
                    ))
                    fig_rsi.add_hline(y=70, line=dict(color='red', width=1, dash='dash'), annotation_text="Overbought", annotation_position="top left")
                    fig_rsi.add_hline(y=30, line=dict(color='green', width=1, dash='dash'), annotation_text="Oversold", annotation_position="bottom left")
                    tick_vals_rsi = rsi_data.index[::30]
                    tick_text_rsi = [date.strftime("%b %Y") for date in tick_vals_rsi]
                    fig_rsi.update_layout(
                        title={"text":f"RSI Chart", "font": {"size": 30}},
                        xaxis_title="Date",
                        yaxis_title="RSI",
                        xaxis=dict(
                            type="category",
                            ticktext=tick_text_rsi,
                            tickvals=tick_vals_rsi,
                            showgrid=True
                        ),
                        yaxis=dict(range=[0, 100])
                    )
                    #
                    if macd_latest > signal_latest:
                        macd_signal = f"🟢  The Moving Averages Convergence Divergence (MACD) indicator for {ticker} is {macd_latest:.2f} and the signal line is at {signal_latest:.2f}, suggesting it is a BUY signal."
                        macd_shortsignal = "Buy"
                    else:
                        macd_signal = f"🔴  The Moving Averages Convergence Divergence (MACD) indicator for {ticker} is {macd_latest:.2f} and the signal line is at {signal_latest:.2f}, suggesting it is a SELL signal."
                        macd_shortsignal = "Sell"
                    if macd_latest_bullish:
                        crossover_signal = "🟢  Bullish Crossover: MACD line crossed above the signal line."
                    elif macd_latest_bearish:
                        crossover_signal = "🔴  Bearish Crossover: MACD line crossed below the signal line."
                    else:
                        crossover_signal = "🔵  No recent crossover detected."
                    #
                    if latest_rsi < 30:
                        rsi_signal = f"🟢  {ticker}'s Relative Strength Index (RSI) is {latest_rsi:.2f}, suggesting a BUY signal."
                        rsi_shortsignal = "Buy"
                    elif 30 <= latest_rsi <= 70:
                        rsi_signal = f"🔵  {ticker}'s Relative Strength Index (RSI) is {latest_rsi:.2f}, suggesting a NEUTRAL."
                        rsi_shortsignal = "Neutral"
                    else:
                        rsi_signal = f"🔴  {ticker}'s Relative Strength Index (RSI) is {latest_rsi:.2f}, suggesting a SELL signal."
                        rsi_shortsignal = "Sell"

                    try:
                        if latest_rsi > 70:
                            if prev_rsi >= latest_rsi:
                                trend_analysis = "🔴  The RSI is above 70 and declining, indicating a potential reversal from overbought."
                            else:
                                trend_analysis = "🔴  The RSI is above 70 and holding, indicating continued overbought conditions."
                        elif latest_rsi < 30:
                            if prev_rsi <= latest_rsi:
                                trend_analysis = "🟢  The RSI is below 30 and rising, indicating a potential reversal from oversold."
                            else:
                                trend_analysis = "🟢  The RSI is below 30 and holding, indicating continued oversold conditions."
                        elif 30 < latest_rsi < 70:
                            if latest_rsi < 50 and prev_rsi < latest_rsi:
                                trend_analysis = "🔺  The RSI is approaching 50 from below, indicating strengthening momentum toward neutral."
                            elif latest_rsi < 50 and prev_rsi > latest_rsi:
                                trend_analysis = "🔻  The RSI is approaching 30 from neutral, indicating weakening momentum toward oversold condition."
                            elif latest_rsi < 50 and prev_rsi == latest_rsi:
                                trend_analysis = "🔻  The RSI is approaching 30 from neutral, indicating weakening momentum toward oversold condition."
                            elif latest_rsi > 50 and prev_rsi > latest_rsi:
                                trend_analysis = "🔻  The RSI is approaching 50 from above, indicating weakening momentum."
                            elif latest_rsi > 50 and prev_rsi < latest_rsi:
                                trend_analysis = "🔺  The RSI is approaching 70 from neutral, indicating strengthening momentum toward overbought condition."
                            elif latest_rsi > 50 and prev_rsi == latest_rsi:
                                trend_analysis = "🔺  The RSI is approaching 70 from neutral, indicating strengthening momentum toward overbought condition."
                    except: trend_analysis = ""
                    #
                    overall_col1, overall_col2 = st.columns ([2,3])
                    with overall_col1:
                        st.plotly_chart(create_gauge("Overall Consensus", overall_score))
                    with overall_col2:
                        latest_data =  ta_data[['STOCH', 'ADX', 'Williams %R', 'CCI', 'ROC', 'UO', 
                        'STOCH Consensus', 'ADX Consensus', 'Williams %R Consensus', 
                        'CCI Consensus', 'ROC Consensus', 'UO Consensus']].iloc[-1]
                        indicator_names = ['SMA20','SMA50', 'SMA200', 'RSI', 'MACD', 'Stochastic Oscillator (STOCH)', 'Average Directional Index (ADX)', 'Williams %R', 'Commodity Channel Index (CCI)', 'Rate of Change (ROC)', 'Ultimate Oscillator (UO)']
                        indicator_values = extended_data['SMA20'].iloc[-1], extended_data['SMA50'].iloc[-1], extended_data['SMA200'].iloc[-1], latest_rsi, macd_latest, *latest_data[['STOCH', 'ADX', 'Williams %R', 'CCI', 'ROC', 'UO']].values
                        indicator_signals = get_shortsignal(price, data['SMA20'][-1], 20), get_shortsignal(price, data['SMA50'][-1], 50), get_shortsignal(price, data['SMA200'][-1], 200), rsi_shortsignal, macd_shortsignal, *latest_data[['STOCH Consensus', 'ADX Consensus', 'Williams %R Consensus', 
                                                        'CCI Consensus', 'ROC Consensus', 'UO Consensus']].values
                        formatted_values = [f"{value:.2f}" for value in indicator_values]
                        summary_df = pd.DataFrame({
                            'Technical Indicator': indicator_names,
                            'Value': formatted_values,
                            'Signal': indicator_signals
                        })
                        st.dataframe(summary_df,hide_index=True,use_container_width=True)
                    #st.subheader("",divider = 'gray')

                    macol1, macol2 = st.columns([3,1])
                    with macol1:
                        st.plotly_chart(fig)
                    with macol2:
                        st.plotly_chart(create_gauge("Moving Average Consensus", ma_score))
                    ma_tcol1, ma_tcol2 = st.columns([3,3]) 
                    with ma_tcol1:
                        st.write(get_signal(price, data['SMA20'][-1], 20))
                        st.write(get_signal(price, data['SMA50'][-1], 50))
                        st.write(get_signal(price, data['SMA200'][-1], 200))
                        if cross_20_50:
                            st.write(cross_20_50)
                        else:
                            st.write("🔵  No recent 20-50 SMAs crossover detected.")
                        if cross_50_200:
                            st.write(cross_50_200)
                        else:
                            st.write("🔵  No recent 50-200 SMAs crossover detected.")
                    with ma_tcol2:
                        st.info("SMAs calculate the average price over a period, treating all past prices equally. If the current stock price is above the SMA, it suggests a buy signal, as the price is above the historical average for that period. A sell signal is suggested when the current price is below the SMA.")
                    st.subheader("",divider = 'gray')

                    mdcol1, mdcol2 = st.columns([3,1])
                    with mdcol1:
                        st.plotly_chart(fig_macd)
                    with mdcol2:
                        st.plotly_chart(create_gauge("MACD Consensus", macd_score))
                    md_tcol1, md_tcol2 = st.columns([3,3])
                    with md_tcol1:
                        st.write(macd_signal)
                        st.write(crossover_signal)
                    with md_tcol2:
                        st.info("The MACD Line is above the Signal Line, indicating a bullish crossover and the stock might be trending upward, so we interpret this as a Buy signal. When the MACD Line is below the Signal Line, it means bearish crossover and the stock might be trending downward, so we interpret this as a Sell signal.")
                    st.subheader("",divider = 'gray')

                    rsicol1, rsicol2 = st.columns([3,1])
                    with rsicol1:
                        st.plotly_chart(fig_rsi)
                    with rsicol2:
                        st.plotly_chart(create_gauge("RSI Consensus", rsi_score))
                    rsi_tcol1, rsi_tcol2 = st.columns([3,3])
                    with rsi_tcol1:
                        st.write(rsi_signal)
                        st.write(trend_analysis)
                    with rsi_tcol2:
                        st.info("If RSI > 70, it generally indicates an Overbought condition. If RSI < 30, it generally indicates an Oversold condition. If RSI is between 30 and 70, it indicates a Neutral condition.")
                    #st.subheader("",divider = 'gray')
            except Exception as e: st.warning(e)

            ###Finviz picture
            # st.subheader("Price Data", divider ='gray')
            # pcol1, pcol2, pcol3 = st.columns ([0.5,3,0.5])
            # with pcol2:
            #     st.image(f'https://finviz.com/chart.ashx?t={ticker}')
            #     st.caption("Chart picture is obtained from finviz.com.")
    except Exception as e:
        st.error(f"Failed to fetch data. Please check your ticker again.")
        st.warning("This tool supports only tickers from the U.S. stock market. Please note that ETFs and cryptocurrencies are not available for analysis. If the entered ticker is valid but the tool does not display results, it may be due to missing data or a technical issue. Kindly try again later. If the issue persists, please contact the developer for further assistance.")
''
