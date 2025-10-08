import streamlit as st
import pandas as pd
from fredapi import Fred 
from groq import Groq
import re

st.set_page_config(layout="wide")

FRED_API_KEY = st.secrets["FRED_API_KEY"]
fred = Fred(api_key=FRED_API_KEY)
ai_model = 'llama-3.3-70b-versatile'

SERIES_MAP = {
    'GDPC1': 'Real GDP',
    'PAYEMS': 'Non-farm Payroll',
    'INDPRO': 'Industrial Production',
    'CPIAUCSL': 'Consumer Price Index',
    'UNRATE': 'Unemployment Rate',
    'T10Y2Y': 'Yield Curve (10Y-2Y Spread)',
    'M2SL': 'Money Supply (M2)',
    'UMCSENT': 'Consumer Sentiment Index',
    'GFDEGDQ188S': 'Debt to GDP Ratio',
    'DFF': 'FED Fund Rate',
    'FPCPITOTLZGUSA': 'Inflation (Annual % Chg)'
}

LATEST_OBSERVATIONS = 30

@st.cache_data(ttl=3600)
def get_latest_fred_data_and_process(series_map, n_obs):
    """
    Fetches the latest N data points for each FRED series,
    aligns them to monthly frequency, and forward-fills missing values.
    """
    df_combined = pd.DataFrame()
    
    for series_id, series_name in series_map.items():
        try:
            start_date = pd.to_datetime('today') - pd.DateOffset(years=2, months=6)
            series = fred.get_series(series_id, observation_start=start_date.strftime('%Y-%m-%d'))
            processed_series = series.resample('MS').mean()    
            df_temp = processed_series.to_frame(name=series_name)
            if df_combined.empty:
                df_combined = df_temp
            else:
                df_combined = pd.merge(df_combined, df_temp, how='outer', left_index=True, right_index=True)
        except Exception as e:
            st.warning(f"Could not fetch or process series **{series_name}** ({series_id}): {e}")
            continue
    df_combined = df_combined.sort_index()
    df_combined = df_combined.ffill()
    df_combined = df_combined.tail(n_obs)
    df_combined = df_combined.reset_index().rename(columns={'index': 'Date'})
    df_combined['Date'] = df_combined['Date'].dt.strftime('%Y-%m-%d')
    return df_combined

st.title("Latest Macroeconomic Data Compilation from FRED API 📈")
st.caption(f"Showing the **latest {LATEST_OBSERVATIONS} months** of data aligned to a **Monthly** frequency.")

try:
    with st.spinner(f'Fetching and processing the latest {LATEST_OBSERVATIONS} months of FRED data...'):
        df_latest = get_latest_fred_data_and_process(SERIES_MAP, LATEST_OBSERVATIONS)   
    if not df_latest.empty:
        st.subheader(f"Latest {LATEST_OBSERVATIONS} Monthly Economic Time Series Data") 
        st.dataframe(df_latest, use_container_width=True) 
    else:
        st.error("No data could be retrieved. Please check your API key and network connection.")

    analysis = ""
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
        summary_prompt = f"""
            Analyze the economic data. Provide:
            - current U.S. economic condition (expansion, moving to peak, peak, moving to contraction, contraction, moving to trough, trough, moving to expansion) with explanations 
            - the concluded answer with this format: Economic Cycle level - [expansion or moving to peak or peak or moving to contraction or contraction or moving to trough or trough or moving to expansion]
            """

        def analyze_stock(prompt_text, tokens):
            response = client.chat.completions.create(
                model=ai_model,
                messages=[
                    {"role": "system", "content": "You are an experienced financial analyst with expertise in both fundamental and technical analysis."},
                    {"role": "user", "content": prompt_text}
                ],
                max_tokens= tokens,
                temperature=0.7
            )
                    
            raw_response = response.choices[0].message.content
            try:
                cleaned_response = re.sub(r'<think>.*?</think>', '', raw_response, flags=re.DOTALL).strip()
            except: 
                cleaned_response = raw_response
            return cleaned_response
        summary_analysis = analyze_stock(summary_prompt,10000)
        analysis = {
            'summary': summary_analysis,
        }
    except Exception as e:
        analysis = ""

    try:
        with st.spinner('Analyzing stock data...'):
            cleaned_text = analysis['summary'].replace('\\n', '\n').replace('\\', '')
            special_chars = ['$', '>', '<', '`', '|', '[', ']', '(', ')', '+', '{', '}', '!', '&']
            for char in special_chars:
                cleaned_text = cleaned_text.replace(char, f"\\{char}")
            st.markdown(cleaned_text, unsafe_allow_html=True)
    except Exception as e:
        st.warning("AI analysis is currently unavailable.")
    
except Exception as e:
    st.error(f"An error occurred: {e}")
