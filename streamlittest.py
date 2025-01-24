import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

st.title('Stock Historical Price Data')

# Create input field and button
ticker = st.text_input('Enter Stock Ticker:', 'AAPL')
fetch_data = st.button('Get Data')

if fetch_data:
    try:
        # Set date range
        end_date = datetime.today()
        start_date = end_date - timedelta(days=365)  # 1 year of data
        
        # Fetch data
        stock_data = yf.download(
            ticker,
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval="1d"
        )
        
        if stock_data.empty:
            st.error(f"No data found for ticker {ticker}")
        else:
            # Display the data
            st.write(f"### Historical Data for {ticker}")
            st.dataframe(stock_data)
            
            # Display basic statistics
            st.write("### Summary Statistics")
            st.dataframe(stock_data.describe())
            
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")