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

st.set_page_config(page_title='AI Stock Analysis', layout='wide', page_icon="./Image/logo.png")

@st.cache_data(ttl=3600)
def get_stock_data(ticker, apiKey=None):

    stock = yf.Ticker(ticker)
    lowercase_ticker = ticker.lower()
    upper_ticker = ticker.upper()
    price = stock.info.get('currentPrice', 'N/A')
    picture_url = f'https://logos.stockanalysis.com/{lowercase_ticker}.svg'
    exchange = stock.info.get('exchange', 'N/A')
    name = stock.info.get('longName', 'N/A')
    sector = stock.info.get('sector', 'N/A')
    industry = stock.info.get('industry', 'N/A')
    employee = stock.info.get('fullTimeEmployees', 'N/A')
    marketCap = stock.info.get('marketCap', 'N/A')
    beta = stock.info.get('beta', 'N/A')
    longProfile = stock.info.get('longBusinessSummary', 'N/A')
    eps = stock.info.get('trailingEps', 'N/A')
    pegRatio = stock.info.get('pegRatio', stock.info.get('trailingPegRatio', 'N/A'))
    country = stock.info.get('country', 'N/A')
    yf_targetprice = stock.info.get('targetMeanPrice', 'N/A')
    yf_consensus = stock.info.get('recommendationKey', 'N/A')
    yf_analysts_count = stock.info.get('numberOfAnalystOpinions', 'N/A')
    website = stock.info.get('website', 'N/A')
    peRatio = stock.info.get('trailingPE', 'N/A')
    forwardPe = stock.info.get('forwardPE', 'N/A')
    dividendYield = stock.info.get('dividendYield', 'N/A')
    payoutRatio = stock.info.get('payoutRatio', 'N/A')
    sharesOutstanding = stock.info.get('sharesOutstanding', 'N/A')
    pbRatio = stock.info.get('priceToBook','N/A')
    deRatio = stock.info.get('debtToEquity','N/A')
    dividends = stock.info.get('dividendRate','N/A')
    exDividendDate = stock.info.get('exDividendDate','N/A')
    roe = stock.info.get('returnOnEquity','N/A')
    revenue_growth_current = stock.info.get('revenueGrowth','N/A')
    profitmargin = stock.info.get('profitMargins','N/A')
    grossmargin = stock.info.get('grossMargins','N/A')
    operatingmargin = stock.info.get('operatingMargins','N/A')
    ebitdamargin = stock.info.get('ebitdaMargins','N/A')
    fcf = stock.info.get('freeCashflow','N/A')
    revenue = stock.info.get('totalRevenue', 'N/A')
    roa = stock.info.get('returnOnAssets','N/A')
    current_ratio = stock.info.get('currentRatio','N/A')
    quick_ratio = stock.info.get('quickRatio','N/A')
    revenue_growth = stock.info.get('revenueGrowth', 'N/A')
    earnings_growth = stock.info.get('earningsGrowth', 'N/A')
    ev_to_ebitda = stock.info.get('enterpriseToEbitda', 'N/A')
    news = stock.news
    try:
        hdata = stock.history(period='max')
        previous_close = hdata['Close'].iloc[-2]
    except: previous_close = 'N/A'
    try:
        income_statement_tb = stock.income_stmt
        quarterly_income_statement_tb = stock.quarterly_income_stmt
    except: income_statement_tb = quarterly_income_statement_tb = ""
    try:
        balance_sheet_tb = stock.balance_sheet
        quarterly_balance_sheet_tb = stock.quarterly_balance_sheet
    except: balance_sheet_tb = quarterly_balance_sheet_tb = ""
    try:
        cashflow_statement_tb = stock.cashflow
        quarterly_cashflow_statement_tb = stock.quarterly_cashflow
    except: cashflow_statement_tb = quarterly_cashflow_statement_tb = ""
    try:
        end_date = datetime.datetime.today()
        start_date = (end_date - datetime.timedelta(days=int(2 * 365)))
        start_date_1y = (end_date - datetime.timedelta(days=int(1 * 365)))
        extended_data_r = yf.download(ticker, start=start_date.strftime('%Y-%m-%d'), end=end_date.strftime('%Y-%m-%d'), interval="1d")
        extended_data_r.columns = extended_data_r.columns.map('_'.join)
        extended_data_r.columns = ['Close', 'High', 'Low', 'Open', 'Volume']
    except: end_date = extended_data_r = ""

    ##### Data Processing #####
    try: change_dollar = price - previous_close
    except: change_dollar = 'N/A'
    try: change_percent = (change_dollar / previous_close) * 100
    except: change_percent = 'N/A'
    try: eps_yield = eps/price
    except: eps_yield = 'N/A'
    employee_value = 'N/A' if employee == 'N/A' else f'{employee:,}'
    marketCap_value = 'N/A' if marketCap == 'N/A' else f'${marketCap/1000000:,.2f}'
    sharesOutstanding_value = 'N/A' if sharesOutstanding == 'N/A' else f'{sharesOutstanding/1000000000:,.2f}B'
    eps_value = 'N/A' if eps == 'N/A' else f'{eps:,.2f}'
    try: pegRatio_value = 'N/A' if pegRatio == 'N/A' else f'{pegRatio:,.2f}'
    except: pegRatio_value = 'N/A'
    beta_value = 'N/A' if beta == 'N/A' else f'{beta:.2f}'
    roe_value = 'N/A' if roe == 'N/A' else f'{roe*100:.2f}%'
    pe_value = 'N/A' if peRatio == 'N/A' else f'{peRatio:.2f}'
    forwardPe_value = 'N/A' if forwardPe == 'N/A' else f'{forwardPe:.2f}'
    pbRatio_value = 'N/A' if pbRatio == 'N/A' else f'{pbRatio:.2f}'
    deRatio_value = 'N/A' if deRatio == 'N/A' else f'{deRatio/100:.2f}'
    revenue_growth_current_value = 'N/A' if revenue_growth_current == 'N/A' else f'{revenue_growth_current*100:.2f}%'
    if fcf == 'N/A' or revenue == 'N/A': fcf_margin = 'N/A'
    else: fcf_margin = (fcf/revenue)
    if grossmargin is None or grossmargin == 'N/A': grossmargin_value = 'N/A'
    else:
        try: grossmargin_value = float(grossmargin)
        except ValueError: grossmargin_value = 'N/A'
    if operatingmargin is None or operatingmargin == 'N/A': operatingmargin_value = 'N/A'
    else:
        try: operatingmargin_value = float(operatingmargin)
        except ValueError: operatingmargin_value = 'N/A'
    if profitmargin is None or profitmargin == 'N/A': profitmargin_value = 'N/A'
    else:
        try: profitmargin_value = float(profitmargin)
        except ValueError: profitmargin_value = 'N/A'
    dividends_value = 'N/A' if dividends == 'N/A' else f'${dividends:,.2f}'
    dividendYield_value = 'N/A' if dividendYield == 'N/A' else f'{dividendYield*100:.2f}%'
    payoutRatio_value = 'N/A' if payoutRatio == 'N/A' else f'{payoutRatio:.2f}'
    if exDividendDate == 'N/A': exDividendDate_value = 'N/A'
    else: 
        exDate = datetime.datetime.fromtimestamp(exDividendDate)
        exDividendDate_value = exDate.strftime('%Y-%m-%d')
    eps_yield_value = 'N/A' if eps_yield == 'N/A' else f'{eps_yield * 100:.2f}%'
    try: 
        income_statement = income_statement_tb  
        quarterly_income_statement = quarterly_income_statement_tb
        ttm = quarterly_income_statement.iloc[:, :4].sum(axis=1)
        income_statement.insert(0, 'TTM', ttm)
        income_statement_flipped = income_statement.iloc[::-1]
    except: income_statement_flipped =''
    try:
        balance_sheet = balance_sheet_tb
        quarterly_balance_sheet = quarterly_balance_sheet_tb
        ttm = quarterly_balance_sheet.iloc[:, :4].sum(axis=1)
        balance_sheet.insert(0, 'TTM', ttm)
        balance_sheet_flipped = balance_sheet.iloc[::-1]
    except: balance_sheet_flipped = ''
    try:
        cashflow_statement = cashflow_statement_tb
        quarterly_cashflow_statement = quarterly_cashflow_statement_tb
        ttm = quarterly_cashflow_statement.iloc[:, :4].sum(axis=1)
        cashflow_statement.insert(0, 'TTM', ttm)
        cashflow_statement_flipped = cashflow_statement.iloc[::-1]
    except: cashflow_statement_flipped = ''
    ##### Data Processing End #####
    
    ##### AI Analysis #####
    try:
        api_key = st.secrets["GROQ_API_KEY"]
        client = Groq(api_key=api_key)
        summary_prompt = f"""
            Analyze the stock {upper_ticker} for both long-term and short-term investment potential. Use the following financial data:
            - Historical price data: {extended_data_r}
            - Key financial metrics: 
                - Valuation: P/E Ratio = {peRatio}, P/B Ratio = {pbRatio}, EV/EBITDA = {ev_to_ebitda}
                - Profitability: Net profit margin = {profitmargin}, ROE = {roe}, ROA = {roa}, Gross margin = {grossmargin}
                - Growth: Revenue growth = {revenue_growth}, Earnings growth = {earnings_growth}
                - Financial health: Debt-to-equity = {deRatio}, Current ratio = {current_ratio}, Quick ratio = {quick_ratio}
                - Cash flow: Free cash flow = {fcf}, Operating cash flow margin = {operatingmargin}
                - Dividends: Dividend yield = {dividendYield}, Dividend payout ratio = {payoutRatio}
            - Income Statement data: {income_statement_tb}
            - Balance Sheet data: {balance_sheet_tb}
            - Cashflow Statement data: {cashflow_statement_tb}
                    
            Provide the following information in Myanmar(Burmese) language:
            1. A summary of whether the stock is good to invest in or not.
            2. Key fundamental analysis metrics (e.g., P/E ratio, revenue growth, debt-to-equity).
            3. Key technical analysis insights (e.g., moving averages, RSI, support/resistance levels).
            4. Sentiment analysis based on news and social media.
            5. Recommendations for when to buy (e.g., based on technical indicators or valuation).
            6. Separate conclusions for long-term and short-term investment strategies.
            """

        def analyze_stock(prompt_text, tokens):
            response = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
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
        summary_analysis = analyze_stock(summary_prompt,100000)
        analysis = {
            'summary': summary_analysis,
        }
    except Exception as e:
        analysis = ""

    try:
        api_key = st.secrets["GROQ_API_KEY3"]
        client = Groq(api_key=api_key)
        snowflake_prompt = f"""
            Analyze the stock {upper_ticker} and rate each category on a scale of 1 to 5 (where 1 is worst and 5 is best). Use the following financial data:
            - Historical price data: {extended_data_r}
            - Key financial metrics: 
                - Valuation: P/E Ratio = {peRatio}, P/B Ratio = {pbRatio}, EV/EBITDA = {ev_to_ebitda}
                - Profitability: Net profit margin = {profitmargin}, ROE = {roe}, ROA = {roa}, Gross margin = {grossmargin}
                - Growth: Revenue growth = {revenue_growth}, Earnings growth = {earnings_growth}
                - Financial health: Debt-to-equity = {deRatio}, Current ratio = {current_ratio}, Quick ratio = {quick_ratio}
                - Cash flow: Free cash flow = {fcf}, Operating cash flow margin = {operatingmargin}
                - Dividends: Dividend yield = {dividendYield}, Dividend payout ratio = {payoutRatio}
            - Income Statement data: {income_statement_tb}
            - Balance Sheet data: {balance_sheet_tb}
            - Cashflow Statement data: {cashflow_statement_tb}
                    
            Provide ONLY these 5 numbers in the exact format below (no other text):
            stock_current_price_valuation:X
            future_performance:X
            past_performance:X
            company_health:X
            dividend:X

            Each rating must be an integer between 1 and 5, where:
            5 = Excellent
            4 = Good
            3 = Average
            2 = Below Average
            1 = Poor
            """

        def analyze_stock3(prompt_text, tokens):
            response = client.chat.completions.create(
                model="deepseek-r1-distill-llama-70b",
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
        snowflake_analysis = analyze_stock3(snowflake_prompt,1000)
        analysis3 = {
            'snowflakes': snowflake_analysis,
        }
    except Exception as e:
        analysis3 = ""
    
    return analysis3, analysis, cashflow_statement_flipped, balance_sheet_flipped, income_statement_flipped, eps_yield_value, exDividendDate_value, payoutRatio_value, dividendYield_value, dividends_value, profitmargin_value, operatingmargin_value, grossmargin_value, fcf_margin, revenue_growth_current_value, deRatio_value, pbRatio_value, forwardPe_value, pe_value, roe_value, beta_value, pegRatio_value, eps_value, sharesOutstanding_value, marketCap_value, employee_value, eps_yield, change_percent, change_dollar,extended_data_r, news, ev_to_ebitda, earnings_growth, revenue_growth, quick_ratio, current_ratio, roa, revenue, fcf, ebitdamargin, operatingmargin, grossmargin, profitmargin, revenue_growth_current, roe, exDividendDate, dividends, deRatio, pbRatio, sharesOutstanding, payoutRatio, dividendYield, forwardPe, peRatio, website, yf_analysts_count, lowercase_ticker, upper_ticker, price, picture_url, exchange, name, sector, industry, employee, marketCap, beta, longProfile, eps, pegRatio, country, yf_targetprice, yf_consensus

''
''
#############################################        #############################################
############################################# Inputs #############################################
#############################################        #############################################

main_col1, main_col2 = st.columns([3,1])
with main_col1:
    st.title("AI Stock Analysis (မြန်မာဘာသာ)")
    input_col1, input_col2, input_col3 = st.columns([1, 3, 1])
    with input_col1:
        ticker = st.text_input("US Stock Ticker ထည့်ရန်:", "AAPL")

st.write("ဤစာမျက်နှာရှိ အချက်အလက်များသည် ပညာရေးဆိုင်ရာ ရည်ရွယ်ချက်များအတွက်သာ ဖြစ်ပြီး၊ ရင်းနှီးမြှုပ်နှံမှုဆိုင်ရာ အကြံပြုချက် သို့မဟုတ် မည်သည့်ရှယ်ယာကိုမဆို ဝယ်ယူရန်/ရောင်းချရန် အကြံပြုခြင်းမဟုတ်ပါ။ ဤအချက်အလက်များကိုအခြေခံ၍ အရောင်းအဝယ်ဆုံးဖြတ်ချက်များကြောင့် ဖြစ်ပေါ်လာသော ဆုံးရှုံးမှုများအတွက် တာဝန်ယူမည်မဟုတ်ပါ။")
st.info('အချက်အလက်များကို Yahoo Finance မှအဓိကရယူထားပြီး deepseek-r1-distill-llama-70b model ဖြင့်စိစစ်ထားပါသည်။')

if st.button("AIဖြင့်စိစစ်ရန်"):
    try:
        analysis3, analysis, cashflow_statement_flipped, balance_sheet_flipped, income_statement_flipped, eps_yield_value, exDividendDate_value, payoutRatio_value, dividendYield_value, dividends_value, profitmargin_value, operatingmargin_value, grossmargin_value, fcf_margin, revenue_growth_current_value, deRatio_value, pbRatio_value, forwardPe_value, pe_value, roe_value, beta_value, pegRatio_value, eps_value, sharesOutstanding_value, marketCap_value, employee_value, eps_yield, change_percent, change_dollar,extended_data_r, news, ev_to_ebitda, earnings_growth, revenue_growth, quick_ratio, current_ratio, roa, revenue, fcf, ebitdamargin, operatingmargin, grossmargin, profitmargin, revenue_growth_current, roe, exDividendDate, dividends, deRatio, pbRatio, sharesOutstanding, payoutRatio, dividendYield, forwardPe, peRatio, website, yf_analysts_count, lowercase_ticker, upper_ticker, price, picture_url, exchange, name, sector, industry, employee, marketCap, beta, longProfile, eps, pegRatio, country, yf_targetprice, yf_consensus = get_stock_data(ticker)
    
        st.header(f'{name}', divider='gray')
        st.subheader("AI Stock Analysis", divider ='gray')
        aicol1, aicol2 = st.columns([3,2])
        with aicol2:
            try:
                response_text = analysis3['snowflakes']
                ratings_dict = {}
                for line in response_text.strip().split('\n'):
                    if ':' in line:
                        category, value = line.split(':')
                        ratings_dict[category.strip()] = int(value.strip())
                stock_current_value = ratings_dict.get('stock_current_value', 0)
                future_performance = ratings_dict.get('future_performance', 0)
                past_performance = ratings_dict.get('past_performance', 0)
                company_health = ratings_dict.get('company_health', 0)
                dividend = ratings_dict.get('dividend', 0)
                radfig = go.Figure()
                radfig.add_trace(go.Scatterpolar(
                    r=[dividend, future_performance, past_performance, company_health, stock_current_value],
                    theta=['အမြတ်ခွဲဝေပေးမှု', 'အနာဂတ်စွမ်းဆောင်ရည်', 'အတိတ်ကစွမ်းဆောင်ရည်', 'ငွေကြေးကျန်းမာရေး', 'ရှယ်ယာပေါက်ဈေးတန်ဖိုး'],
                    fill='toself',
                    name='Stock Analysis',
                    line_color='#FFA500', 
                    fillcolor='rgba(255, 165, 0, 0.2)',
                ))
                radfig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 5],
                            showticklabels=False,
                        ),
                        bgcolor='rgba(0,0,0,0)'
                    ),
                    showlegend=False,
                    #title='Stock Analysis Ratings',
                    #paper_bgcolor='rgba(0,0,0,0)',
                    margin=dict(t=100, b=100, l=100, r=100),
                )
                st.plotly_chart(radfig)
            except Exception as e:
                st.write("")
            ''
            aisubcol1, aisubcol2, aisubcol3 = st.columns([1,3,3])
            with aisubcol2:
                st.metric(label='Current Price',value=f'${price:,.2f}')
                st.metric(label='EPS (ttm)',value=eps_value)
                st.metric(label='ROE',value=roe_value)
                st.metric(label='Gross Margin',value=f"{grossmargin_value * 100:.1f}%")
            with aisubcol3:
                st.metric(label='PE Ratio',value=pe_value)
                st.metric(label='DE Ratio',value=deRatio_value)
                st.metric(label='Revenue Growth',value=revenue_growth_current_value)
                st.metric(label='Profit Margin',value=f"{profitmargin_value * 100:.1f}%")
                    
        with aicol1:
            try:
                if upper_ticker:
                    with st.spinner('Analyzing stock data...'):
                        cleaned_text = analysis['summary'].replace('\\n', '\n').replace('\\', '')
                        special_chars = ['$', '>', '<', '`', '|', '[', ']', '(', ')', '+', '{', '}', '!', '&']
                        for char in special_chars:
                            cleaned_text = cleaned_text.replace(char, f"\\{char}")
                        st.markdown(cleaned_text, unsafe_allow_html=True)
            except Exception as e:
                st.warning("AI analysis is currently unavailable.")
                            
        st.warning("This analysis, generated by AI, should not be the sole basis for investment decisions.")

    except Exception as e:
        st.write(e)
        st.error(f"Failed to fetch data. Please check your ticker again.")
        st.warning("This tool supports only tickers from the U.S. stock market. Please note that ETFs and cryptocurrencies are not available for analysis. If the entered ticker is valid but the tool does not display results, it may be due to missing data or a technical issue. Kindly try again later. If the issue persists, please contact the developer for further assistance.")
''
