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

st.set_page_config(page_title='US Stock Analysis Tool', layout='wide', page_icon="./Image/logo.png")
@st.cache_data(ttl=3600)
def get_stock_data(ticker, apiKey=None, use_ai=True):

############################                           ##############################
############################ Getting Stock Information ##############################
############################                           ##############################
    
    stock = yf.Ticker(ticker)
    lowercase_ticker = ticker.lower()
    upper_ticker = ticker.upper()
    price = stock.info.get('currentPrice', 'N/A')
    picture_url = f'https://logos.stockanalysis.com/{lowercase_ticker}.svg'
    exchange = stock.info.get('exchange', 'N/A')
    
    #### Exchange Value ####
    if exchange == 'NYQ':
        exchange_value = "NYSE"
    elif exchange == 'NMS':
        exchange_value = "NASDAQ"
    else:
        exchange_value = "N/A"
    lower_exchange = exchange_value.lower()
    ########################

    ##### Morning Star #####
    fair_value = fvDate = moat = moatDate = starRating = assessment = 'N/A'
    performance_id = None
    if apiKey:
        try:
            conn = http.client.HTTPSConnection("morning-star.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': apiKey,
                'x-rapidapi-host': "morning-star.p.rapidapi.com"
            }
            conn.request("GET", "/market/v2/auto-complete?q=" + ticker, headers=headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data.decode("utf-8"))
            for item in json_data.get('results', []):
                if item.get('ticker', '').upper() == ticker.upper():
                    performance_id = item.get('performanceId')
                    break
        except Exception as e:
            print(f"APIkey: Morningstar API request failed.")
            
    if performance_id:
        try:
            conn = http.client.HTTPSConnection("morning-star.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': apiKey,
                'x-rapidapi-host': "morning-star.p.rapidapi.com"
            }
            conn.request("GET", "/stock/v2/get-analysis-data?performanceId="+ performance_id, headers=headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data.decode("utf-8"))
            fair_value = json_data['valuation']['fairValue']
            fvDate = json_data['valuation']['fairValueDate']
            moat = json_data['valuation']['moat']
            moatDate = json_data['valuation']['moatDate']
            starRating = json_data['valuation']['startRating']
            assessment = json_data['valuation']['assessment']
        except Exception as e:
            print("Performance ID: Morningstar API request failed.")
    ########################

    ##### Seeking Alpha #####
    authors_strongsell_count = authors_strongbuy_count = authors_sell_count = authors_hold_count = authors_buy_count = authors_rating = authors_count = epsRevisionsGrade = dpsRevisionsGrade = dividendYieldGrade = divSafetyCategoryGrade = divGrowthCategoryGrade = divConsistencyCategoryGrade = sellSideRating = ticker_id = quant_rating = growth_grade = momentum_grade = profitability_grade = value_grade = yield_on_cost_grade = 'N/A'
    sk_targetprice = 'N/A'
    if apiKey:
        try:
            conn = http.client.HTTPSConnection("seeking-alpha.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': apiKey,
                'x-rapidapi-host': "seeking-alpha.p.rapidapi.com"
            }
            conn.request("GET", "/symbols/get-ratings?symbol=" + ticker, headers=headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data.decode("utf-8"))
            first_data = json_data['data'][0]['attributes']['ratings']
            ticker_id = json_data['data'][0]['attributes']['tickerId']
            #
            quant_rating = first_data['quantRating']
            growth_grade = first_data['growthGrade']
            momentum_grade = first_data['momentumGrade']
            profitability_grade = first_data['profitabilityGrade']
            value_grade = first_data['valueGrade']
            yield_on_cost_grade = first_data['yieldOnCostGrade']
            epsRevisionsGrade = first_data['epsRevisionsGrade']
            dpsRevisionsGrade = first_data['dpsRevisionsGrade']
            dividendYieldGrade = first_data['dividendYieldGrade']
            divSafetyCategoryGrade = first_data['divSafetyCategoryGrade']
            divGrowthCategoryGrade = first_data['divGrowthCategoryGrade']
            divConsistencyCategoryGrade = first_data['divConsistencyCategoryGrade']
            sellSideRating = first_data['sellSideRating']
            #
            authors_count = first_data['authorsCount']
            authors_rating = first_data['authorsRating']
            authors_buy_count = first_data['authorsRatingBuyCount']
            authors_hold_count = first_data['authorsRatingHoldCount']
            authors_sell_count = first_data['authorsRatingSellCount']
            authors_strongbuy_count = first_data['authorsRatingStrongBuyCount']
            authors_strongsell_count = first_data['authorsRatingStrongSellCount']
        except Exception as e:
            print("Analysts Data: Seeking Alpha API request failed.")

    if apiKey and ticker_id and ticker_id != 'N/A':
        ticker_id_str = str(ticker_id)
        try:
            conn = http.client.HTTPSConnection("seeking-alpha.p.rapidapi.com")
            headers = {
                'x-rapidapi-key': apiKey,
                'x-rapidapi-host': "seeking-alpha.p.rapidapi.com"
            }
            conn.request("GET", "/symbols/get-analyst-price-target?ticker_ids=" + ticker_id_str + "&return_window=1&group_by_month=false", headers=headers)
            res = conn.getresponse()
            data = res.read()
            json_data = json.loads(data.decode("utf-8"))
            get_sk_data = json_data['estimates'][f'{ticker_id}']['target_price']['0'][0]
            sk_targetprice = get_sk_data['dataitemvalue']
        except Exception as e:
            print("Price Data: Seeking Alpha API request failed.")
    ########################

    ##### SA forecasts #####
    try:
        url = f'https://stockanalysis.com/stocks/{ticker}/forecast/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text,"html.parser")
        table = soup.find("table",class_ = "sticky-column-table w-full border-separate border-spacing-0 whitespace-nowrap text-right text-sm sm:text-base")
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
    ########################

    ##### SA scores #####
    try:
        sa_score_url = f'https://stockanalysis.com/stocks/{ticker}/statistics/'
        sa_score_response = requests.get(sa_score_url)
        sa_score_soup = BeautifulSoup(sa_score_response.content, "html.parser")
        sa_score_table = sa_score_soup.find_all('table')[17]
        sa_score_data = {}
        #sa_altmanz = "N/A"
        #sa_piotroski = "N/A"
        if sa_score_table:
            rows = sa_score_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:  
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    sa_score_data[key] = value
            sa_altmanz = sa_score_data.get("Altman Z-Score", "N/A")
            sa_piotroski = sa_score_data.get("Piotroski F-Score", "N/A")
    except Exception as e:
        print(f"SA scores fetching failed")
    ########################

    ##### SA analysts rating #####
    try:
        sa_statistics_url = f'https://stockanalysis.com/stocks/{ticker}/statistics/'
        sa_statistics_response = requests.get(sa_statistics_url)
        sa_statistics_soup = BeautifulSoup(sa_statistics_response.content, "html.parser")
        sa_analyst_table = sa_statistics_soup.find_all('table')[15]
        sa_analysts_data = {}
        sa_analysts_consensus = "N/A"
        sa_analysts_targetprice = "N/A"
        sa_analysts_count = "N/A"
        if sa_analyst_table:
            rows = sa_analyst_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) == 2:  
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    sa_analysts_data[key] = value

            sa_analysts_consensus = sa_analysts_data.get("Analyst Consensus", "N/A")
            sa_analysts_targetprice = sa_analysts_data.get("Price Target", "N/A")
            sa_analysts_count = sa_analysts_data.get("Analyst Count", "N/A")
    except Exception as e:
        print("SA analysts data fetching failed.")
    ########################

    ##### Market Beat forecast #####
    try:
        mb_url = f'https://www.marketbeat.com/stocks/{exchange_value}/{upper_ticker}/forecast/'
        mb_response = requests.get(mb_url)
        mb_soup = BeautifulSoup(mb_response.content, "html.parser")
        mb_table = mb_soup.find_all('table')[1]
        mb_data = {}
        mb_consensus_rating = "N/A"
        mb_predicted_upside = "N/A"
        mb_rating_score = "N/A"
        if mb_table:
            rows = mb_table.find_all('tr')
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 2:  
                    key = cols[0].text.strip()
                    value = cols[1].text.strip()
                    mb_data[key] = value
            mb_consensus_rating = mb_data.get("Consensus Rating", "N/A")
            mb_predicted_upside = mb_data.get("Predicted Upside", "N/A")
            mb_rating_score = mb_data.get("Consensus Rating Score", "N/A")
            if mb_predicted_upside != "N/A":
                match = re.search(r"([-+]?\d*\.?\d+)", mb_predicted_upside)
            if match:
                mb_predicted_upside = float(match.group(0))
                mb_targetprice = 'N/A' if mb_predicted_upside == 'N/A' else (price * (mb_predicted_upside + 100)) / 100
                mb_targetprice_value = 'N/A' if mb_targetprice == 'N/A' else f'${mb_targetprice:.2f}'
    except Exception as e:
        mb_targetprice_value = mb_predicted_upside = mb_consensus_rating = mb_rating_score = 'N/A'
    ########################

    ##### Market Beat sector competitors #####
    try:
        mb_com_url = f'https://www.marketbeat.com/stocks/{exchange_value}/{upper_ticker}/competitors-and-alternatives/'
        mb_com_response = requests.get(mb_com_url)
        mb_com_soup = BeautifulSoup(mb_com_response.content, "html.parser")
        mb_com_table = mb_com_soup.find_all('table')[5]
        headers = [header.get_text(strip=True) for header in mb_com_table.find_all('th')]
        headers[2] = "Stock's Industry"
        rows = []
        for row in mb_com_table.find_all('tr')[1:]:
            row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
            rows.append(row_data)
        mb_com_df = pd.DataFrame(rows, columns=headers)
    except: mb_com_df = ""
    ########################

    ##### Market Beat dividend comparison #####
    try:
        mb_com_url = f'https://www.marketbeat.com/stocks/{exchange_value}/{upper_ticker}/dividend/'
        mb_com_response = requests.get(mb_com_url)
        mb_com_soup = BeautifulSoup(mb_com_response.content, "html.parser")
        mb_com_table = mb_com_soup.find_all('table')[0]
        headers = [header.get_text(strip=True) for header in mb_com_table.find_all('th')]
        rows = []
        for row in mb_com_table.find_all('tr')[1:]:
            row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
            rows.append(row_data)
        mb_div_df = pd.DataFrame(rows, columns=headers)
        if mb_div_df.iloc[0, 0] == 'Annual Dividend':
            mb_div_df = mb_div_df
        else:
            mb_div_df = ""
    except: mb_div_df = ""
    ########################

    ##### Market Beat competitors #####
    try:
        mb_com_url = f'https://www.marketbeat.com/stocks/{exchange_value}/{upper_ticker}/competitors-and-alternatives/'
        mb_com_response = requests.get(mb_com_url)
        mb_com_soup = BeautifulSoup(mb_com_response.content, "html.parser")
        mb_com_table = mb_com_soup.find_all('table')[6]
        mb_alt_headers = [mb_alt_header.get_text(strip=True) for mb_alt_header in mb_com_table.find_all('th')]
        rows = []
        for row in mb_com_table.find_all('tr')[1:]:
            row_data = [cell.get_text(strip=True) for cell in row.find_all('td')]
            rows.append(row_data)
        mb_alt_df = pd.DataFrame(rows, columns=mb_alt_headers)
    except: mb_alt_df = mb_alt_headers = ""
    ########################
    
    ##### SA metric table #####
    try:
        url = f'https://stockanalysis.com/stocks/{ticker}/financials/ratios/'
        r = requests.get(url)
        soup = BeautifulSoup(r.text,"html.parser")
        table = soup.find("table",class_ = "w-full border-separate border-spacing-0 text-sm sm:text-base [&_tbody]:sm:whitespace-nowrap [&_thead]:whitespace-nowrap")
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
        sa_metrics_df = pd.DataFrame(data, columns=headers)
        sa_metrics_df = sa_metrics_df.iloc[1:, :-1].reset_index(drop=True)
    except: sa_metrics_df = ""
    ########################

    ##### SA metric table2 #####
    try:
        url2 = f'https://stockanalysis.com/stocks/{ticker}/financials/'
        r2 = requests.get(url2)
        soup2 = BeautifulSoup(r2.text,"html.parser")
        table2 = soup2.find("table",class_ = "w-full border-separate border-spacing-0 text-sm sm:text-base [&_tbody]:sm:whitespace-nowrap [&_thead]:whitespace-nowrap")
        rows2 = table2.find_all("tr")
        headers2 = []
        data2 = []
        for row2 in rows2:
            cols2 = row2.find_all(["th", "td"])
            cols2_text = [col2.text.strip() for col2 in cols2]
            if not headers2:
                headers2 = cols2_text
            else:
                data2.append(cols2_text)
        sa_metrics_df2 = pd.DataFrame(data2, columns=headers2)
        sa_metrics_df2 = sa_metrics_df2.iloc[1:, :-1].reset_index(drop=True)
    except: sa_metrics_df2 = ""
    ########################

    ##### Market Beat insider trades #####
    try:
        insider_mb_url = f'https://www.marketbeat.com/stocks/{exchange_value}/{upper_ticker}/insider-trades/'
        response = requests.get(insider_mb_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        tables = soup.find_all('table')
        if tables and len(tables) > 0:
            table = tables[0]
            headers = []
            rows = []
            for th in table.find_all('th'):
                headers.append(th.text.strip())
            for tr in table.find_all('tr')[1:]:
                row = []
                for td in tr.find_all('td'):
                    row.append(td.text.strip())
                if row: 
                    rows.append(row)
            insider_mb = pd.DataFrame(rows, columns=headers)
            if insider_mb.empty:
                insider_mb = pd.DataFrame()
        else:    
            insider_mb = pd.DataFrame()
    except Exception as e:
        insider_mb = pd.DataFrame()
    ########################

    ##### Yahoo Finance #####
    ##### Profile #####
    name = stock.info.get('longName', 'N/A')
    sector = stock.info.get('sector', 'N/A')
    industry = stock.info.get('industry', 'N/A')
    employee = stock.info.get('fullTimeEmployees', 'N/A')
    marketCap = stock.info.get('marketCap', 'N/A')
    beta = stock.info.get('beta', 'N/A')
    longProfile = stock.info.get('longBusinessSummary', 'N/A')
    country = stock.info.get('country', 'N/A')
    website = stock.info.get('website', 'N/A')
    sharesOutstanding = stock.info.get('sharesOutstanding', 'N/A')
    ##### Earnings #####
    revenue = stock.info.get('totalRevenue', 'N/A')
    eps = stock.info.get('trailingEps', 'N/A')
    pegRatio = stock.info.get('pegRatio', stock.info.get('trailingPegRatio', 'N/A'))
    ##### Price Target #####
    yf_targetprice = stock.info.get('targetMeanPrice', 'N/A')
    yf_consensus = stock.info.get('recommendationKey', 'N/A')
    yf_analysts_count = stock.info.get('numberOfAnalystOpinions', 'N/A')
    ##### Valuation #####
    peRatio = stock.info.get('trailingPE', 'N/A')
    forwardPe = stock.info.get('forwardPE', 'N/A')
    pbRatio = stock.info.get('priceToBook','N/A')
    ev_to_ebitda = stock.info.get('enterpriseToEbitda', 'N/A')
    ##### Dividends #####
    dividendYield = stock.info.get('dividendYield', 'N/A')
    payoutRatio = stock.info.get('payoutRatio', 'N/A')
    dividends = stock.info.get('dividendRate','N/A')
    exDividendDate = stock.info.get('exDividendDate','N/A')
    ##### Financials Health #####
    deRatio = stock.info.get('debtToEquity','N/A')
    current_ratio = stock.info.get('currentRatio','N/A')
    quick_ratio = stock.info.get('quickRatio','N/A')
    ##### Profitability #####
    roe = stock.info.get('returnOnEquity','N/A')
    roa = stock.info.get('returnOnAssets','N/A')
    ##### Margin #####
    profitmargin = stock.info.get('profitMargins','N/A')
    grossmargin = stock.info.get('grossMargins','N/A')
    operatingmargin = stock.info.get('operatingMargins','N/A')
    ebitdamargin = stock.info.get('ebitdaMargins','N/A')
    ##### Cash Flow #####
    fcf = stock.info.get('freeCashflow','N/A')
    ##### Growth #####
    revenue_growth = stock.info.get('revenueGrowth', 'N/A')
    revenue_growth_current = stock.info.get('revenueGrowth','N/A')
    earnings_growth = stock.info.get('earningsGrowth', 'N/A')
    ##### News #####
    news = stock.news
    ##### Sustainability #####
    try: 
        sustainability = stock.sustainability
        if sustainability is not None:   
            totalEsg = sustainability.loc['totalEsg']['esgScores']
            enviScore = sustainability.loc['environmentScore']['esgScores']
            socialScore = sustainability.loc['socialScore']['esgScores']
            governScore = sustainability.loc['governanceScore']['esgScores']
            percentile = sustainability.loc['percentile']['esgScores']
        else:
            totalEsg = enviScore = socialScore = governScore = percentile = "N/A"
    except:
        totalEsg = enviScore = socialScore = governScore = percentile = "N/A"
    ##### Holders #####
    try:
        major_holders = stock.major_holders    
        if major_holders is not None:
            insiderPct = stock.major_holders.loc['insidersPercentHeld']['Value']
            institutionsPct = stock.major_holders.loc['institutionsPercentHeld']['Value']
        else: 
            insiderPct = institutionsPct = "N/A"
    except Exception as e:
        insiderPct = institutionsPct = "N/A"
    ##### Historical Price Data #####
    try:
        hdata = stock.history(period='max')
        previous_close = hdata['Close'].iloc[-2]
    except: previous_close = 'N/A'
    ##### Earnings Date #####
    try:
        get_earningsDate = stock.calendar['Earnings Date']
        if get_earningsDate:
            earningsDate = get_earningsDate[0].strftime('%Y-%m-%d')
        else:
            earningsDate = 'N/A'
    except: earningsDate = 'N/A'
    ##### Historical Dividends Data #####
    try: dividend_history = stock.dividends
    except: dividend_history = ""
    ##### Historical Earnings Data #####
    try: earnings_history = stock.earnings_history
    except: earnings_history = ""
    ##### EPS Trend #####
    try: eps_trend = stock.eps_trend
    except: eps_trend = ""
    ##### Income Statement #####
    try:
        income_statement_tb = stock.income_stmt
        quarterly_income_statement_tb = stock.quarterly_income_stmt
    except: income_statement_tb = quarterly_income_statement_tb = ""
    ##### Balance Sheet #####
    try:
        balance_sheet_tb = stock.balance_sheet
        quarterly_balance_sheet_tb = stock.quarterly_balance_sheet
    except: balance_sheet_tb = quarterly_balance_sheet_tb = ""
    ##### Cashflow Statement #####
    try:
        cashflow_statement_tb = stock.cashflow
        quarterly_cashflow_statement_tb = stock.quarterly_cashflow
    except: cashflow_statement_tb = quarterly_cashflow_statement_tb = ""
    ########################

    ##### Comparison Data Processing #####
    try:
        sector_etf_mapping = {
                    "Consumer Cyclical": "XLY",
                    "Consumer Defensive": "XLP",
                    "Energy": "XLE",
                    "Financial Services": "XLF",
                    "Healthcare": "XLV",
                    "Industrials": "XLI",
                    "Basic Materials": "XLB",
                    "Real Estate": "XLR",
                    "Technology": "XLK",
                    "Utilities": "XLU",
                    "Communication Services": "XLC"
                    }
        matching_etf = sector_etf_mapping.get(sector)
        compare_tickers = (upper_ticker, '^GSPC', matching_etf)
        end = datetime.datetime.today()
        start = end - relativedelta(years=5)
        def relativereturn(df):
            rel = df.pct_change()
            cumret = (1+rel).cumprod()-1
            cumret = cumret.fillna(0)
            return cumret
        yf_com = relativereturn(yf.download(compare_tickers, start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d'))['Close'])
    except: yf_com = matching_etf = ""
    ########################

    ##### Technical Data Processing #####
    try:
        end_date = datetime.datetime.today()
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
    ########################

    ##### Basic Data Processing #####
    ##### Profile #####
    try: change_dollar = price - previous_close #change in price
    except: change_dollar = 'N/A'
    #-----------------------------------------------------------
    try: change_percent = (change_dollar / previous_close) * 100 #change in price pct
    except: change_percent = 'N/A'
    #--------------------------------------------------------------------------------
    employee_value = 'N/A' if employee == 'N/A' else f'{employee:,}' #employee value
    #-------------------------------------------------------------------------------
    marketCap_value = 'N/A' if marketCap == 'N/A' else f'${marketCap/1000000:,.2f}' #market cap value
    #------------------------------------------------------------------------------------------------
    sharesOutstanding_value = 'N/A' if sharesOutstanding == 'N/A' else f'{sharesOutstanding/1000000000:,.2f}B' #shares outstanding value
    #-----------------------------------------------------------------------------------------------------------------------------------
    beta_value = 'N/A' if beta == 'N/A' else f'{beta:.2f}' #beta value
    #-----------------------------------------------------------------
    
    ##### Earnings #####
    try: eps_yield = eps/price #eps yield
    except: eps_yield = 'N/A'
    #------------------------------------
    eps_value = 'N/A' if eps == 'N/A' else f'{eps:,.2f}' #eps value
    #--------------------------------------------------------------
    eps_yield_value = 'N/A' if eps_yield == 'N/A' else f'{eps_yield * 100:.2f}%' #eps yield value
    #--------------------------------------------------------------------------------------------
    try: pegRatio_value = 'N/A' if pegRatio == 'N/A' else f'{pegRatio:,.2f}' #peg ratio value
    except: pegRatio_value = 'N/A'
    #----------------------------------------------------------------------------------------
    
    ##### Target Price #####
    try: yf_mos = ((yf_targetprice - price)/yf_targetprice) * 100 #yf target price mos
    except: yf_mos = 'N/A'
    #---------------------------------------------------------------------------------
    
    ##### Valuation #####
    pe_value = 'N/A' if peRatio == 'N/A' else f'{peRatio:.2f}' #pe ratio value
    #-------------------------------------------------------------------------
    forwardPe_value = 'N/A' if forwardPe == 'N/A' else f'{forwardPe:.2f}' #forward pe ratio value
    #--------------------------------------------------------------------------------------------
    pbRatio_value = 'N/A' if pbRatio == 'N/A' else f'{pbRatio:.2f}' #pb ratio value
    #------------------------------------------------------------------------------
    
    ##### Dividends #####
    dividends_value = 'N/A' if dividends == 'N/A' else f'${dividends:,.2f}' #dividends value
    #---------------------------------------------------------------------------------------
    dividendYield_value = 'N/A' if dividendYield == 'N/A' else f'{dividendYield:.2f}%' #dividend yield value
    #-------------------------------------------------------------------------------------------------------
    payoutRatio_value = 'N/A' if payoutRatio == 'N/A' else f'{payoutRatio:.2f}' #payout ratio value
    #----------------------------------------------------------------------------------------------
    if exDividendDate == 'N/A': exDividendDate_value = 'N/A' #ex dividend date value
    else: 
        exDate = datetime.datetime.fromtimestamp(exDividendDate)
        exDividendDate_value = exDate.strftime('%Y-%m-%d')
    #-------------------------------------------------------------------------------
    
    ##### Financial Health #####
    deRatio_value = 'N/A' if deRatio == 'N/A' else f'{deRatio/100:.2f}' #de ratio value
    #----------------------------------------------------------------------------------
    try: sa_piotroski_value = 'N/A' if sa_piotroski == 'N/A' else float(sa_piotroski) #sa piotroski value
    except: sa_piotroski_value = 'N/A'
    #----------------------------------------------------------------------------------------------------
    try: sa_altmanz_value = 'N/A' if sa_altmanz == 'N/A' else float(sa_altmanz) #sa altmanz value
    except: sa_altmanz_value = 'N/A'
    #--------------------------------------------------------------------------------------------
    
    ##### Profitability #####
    roe_value = 'N/A' if roe == 'N/A' else f'{roe*100:.2f}%' #roe value
    #------------------------------------------------------------------
    roa_value = 'N/A' if roa == 'N/A' else f'{roa*100:.2f}%' #roa value
    #------------------------------------------------------------------
    
    ##### Margin #####
    if grossmargin is None or grossmargin == 'N/A': grossmargin_value = 'N/A' #gross margin value
    else:
        try: grossmargin_value = float(grossmargin)
        except ValueError: grossmargin_value = 'N/A'
    #--------------------------------------------------------------------------------------------
    if operatingmargin is None or operatingmargin == 'N/A': operatingmargin_value = 'N/A' #operating margin value
    else:
        try: operatingmargin_value = float(operatingmargin)
        except ValueError: operatingmargin_value = 'N/A'
    #------------------------------------------------------------------------------------------------------------
    if profitmargin is None or profitmargin == 'N/A': profitmargin_value = 'N/A' #profit margin value
    else:
        try: profitmargin_value = float(profitmargin)
        except ValueError: profitmargin_value = 'N/A'
    #------------------------------------------------------------------------------------------------
    if fcf_margin is None or fcf_margin == 'N/A': fcfmargin_value = 'N/A' #fcf margin value
    else:
        try: fcfmargin_value = float(fcf_margin)
        except ValueError: fcfmargin_value = 'N/A'
    #--------------------------------------------------------------------------------------
    grossmargin_pct = 'N/A' if grossmargin_value == 'N/A' else f'{grossmargin_value*100:.2f}%' #gross margin pct value
    #-----------------------------------------------------------------------------------------------------------------
    operatingmargin_pct = 'N/A' if operatingmargin_value == 'N/A' else f'{operatingmargin_value*100:.2f}%' #operating margin pct value
    #---------------------------------------------------------------------------------------------------------------------------------
    profitmargin_pct = 'N/A' if profitmargin_value == 'N/A' else f'{profitmargin_value*100:.2f}%' #profit margin pct value
    #---------------------------------------------------------------------------------------------------------------------
    
    ##### Cash Flow #####
    if fcf == 'N/A' or revenue == 'N/A': fcf_margin = 'N/A' #fcf margin value
    else: fcf_margin = (fcf/revenue)
    #------------------------------------------------------------------------
    
    ##### Grwoth #####
    earnings_growth_value = 'N/A' if earnings_growth == 'N/A' else f'{earnings_growth*100:.2f}%' #earnings growth value
    #------------------------------------------------------------------------------------------------------------------
    revenue_growth_value = 'N/A' if revenue_growth == 'N/A' else f'{revenue_growth*100:.2f}%' #revenue growth value
    #--------------------------------------------------------------------------------------------------------------
    revenue_growth_current_value = 'N/A' if revenue_growth_current == 'N/A' else f'{revenue_growth_current*100:.2f}%' #revenue growth current value
    #----------------------------------------------------------------------------------------------------------------------------------------------
    
    ##### Holdings #####
    insiderPct_value = 'N/A' if insiderPct == 'N/A' else f'{insiderPct*100:,.2f}%' #insider pct value
    #------------------------------------------------------------------------------------------------
    institutionsPct_value = 'N/A' if institutionsPct == 'N/A' else f'{institutionsPct*100:,.2f}%' #institutions pct value
    #--------------------------------------------------------------------------------------------------------------------
    
    ##### Sustainability #####
    totalEsg_value = 0.00 if totalEsg == 'N/A' else totalEsg #total esg value
    #------------------------------------------------------------------------
    
    ##### Income Statement #####
    try: 
        income_statement = income_statement_tb  
        quarterly_income_statement = quarterly_income_statement_tb
        ttm = quarterly_income_statement.iloc[:, :4].sum(axis=1)
        income_statement.insert(0, 'TTM', ttm)
        income_statement_flipped = income_statement.iloc[::-1]
    except: income_statement_flipped =''
    #-------------------------------------------------------------
    
    ##### Income Statement #####
    try:
        balance_sheet = balance_sheet_tb
        quarterly_balance_sheet = quarterly_balance_sheet_tb
        ttm = quarterly_balance_sheet.iloc[:, :4].sum(axis=1)
        balance_sheet.insert(0, 'TTM', ttm)
        balance_sheet_flipped = balance_sheet.iloc[::-1]
    except: balance_sheet_flipped = ''
    #--------------------------------------------------------
    
    ##### Income Statement #####
    try:
        cashflow_statement = cashflow_statement_tb
        quarterly_cashflow_statement = quarterly_cashflow_statement_tb
        ttm = quarterly_cashflow_statement.iloc[:, :4].sum(axis=1)
        cashflow_statement.insert(0, 'TTM', ttm)
        cashflow_statement_flipped = cashflow_statement.iloc[::-1]
    except: cashflow_statement_flipped = ''
    #-----------------------------------------------------------------
    ##### Data Processing End #####

    ##### AI Analysis #####
    analysis = ""
    analysis2 = ""
    analysis3 = ""
    if use_ai:
        ##### Analysis Summary #####
        try:
            api_key = st.secrets["GROQ_API_KEY"]
            client = Groq(api_key=api_key)
            summary_prompt = f"""
                Analyze the stock {upper_ticker} for both long-term and short-term investment potential. Use the following financial data:
                - Historical price data: {extended_data_r}
                - Key financial metrics: 
                    - Valuation: P/E Ratio = {peRatio}, P/B Ratio = {pbRatio}, EV/EBITDA = {ev_to_ebitda}
                    - Profitability: Net profit margin = {profitmargin_pct}, ROE = {roe_value}, ROA = {roa_value}, Gross margin = {grossmargin_pct}
                    - Growth: Revenue growth = {revenue_growth_value}, Earnings growth = {earnings_growth_value}
                    - Financial health: Debt-to-equity = {deRatio_value}, Current ratio = {current_ratio}, Quick ratio = {quick_ratio}
                    - Cash flow: Free cash flow = {fcf}, Operating cash flow margin = {operatingmargin_pct}
                    - Dividends: Dividend yield = {dividendYield_value}, Dividend payout ratio = {payoutRatio}
                - Income Statement data: {income_statement_tb}
                - Balance Sheet data: {balance_sheet_tb}
                - Cashflow Statement data: {cashflow_statement_tb}
                        
                Provide:
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
        ########################
        
        ##### Financial Statement Analysis #####
        try:
            api_key = st.secrets["GROQ_API_KEY2"]
            client = Groq(api_key=api_key)
            income_statement_prompt = f"""
                You are a financial analyst. Analyze the provided Income Statement Data using {income_statement_flipped} and evaluate the following criteria:
                1. Revenue Growth: the revenue should consistently grow year over year.
                2. Gross Margin: the gross margin should not be declining and should be stable, or increasing.
                3. Operating Expenses: The expenses should not be rising faster than revenue.
                4. Operating Margin: the operating costs should not be rising.
                5. Non-Operating Expenses: non-operating expenses should not be rising.
                6. Net Profit Margin: net profit margin should consistently grow year over year.
                7. EPS Growth: EPS should be positive and growing.
                
                Final Evaluation:
                Based on the analysis, determine whether the company's financial position is strong, stable, or weak for investment. Highlight key risks, strengths, or potential red flags that investors should consider.
                """
                
            balance_sheet_prompt = f"""
                You are a financial analyst. Analyze the provided Balance Sheet Data using {balance_sheet_flipped} and evaluate the following criteria:
                1. Cash & Debt: company should have more cash than total debt.
                2. Accounts Receivable: there should not be accounts receivable.
                3. Inventory: there should not be inventory.
                4. Current Liabilities: current liabilities should be less than cash. 
                5. Short-term or Long-term Debt: there should not be not much short-term or long-term debt.
                6. Goodwill: should be less than 10% of total assets.
                7. Preferred Stocks: there should not be preferred stock.
                8. Retained Earnings: should be positive & growing.
                9. Treasury Stock: should exist.
                
                Final Evaluation:
                Based on this analysis, evaluate the company's financial health, highlighting key strengths, risks, and whether the balance sheet reflects a strong position for investment.
                """
            
            cashflow_statement_prompt = f"""
                You are a financial analyst. Analyze the provided Cash Flow Statement Data using {cashflow_statement_flipped} and evaluate the following criteria:
                1. Net Income: Should be positive and growing.
                2. Stock-Based Compensation: Should be less than 10% of Net Income.
                3. Operating Cash Flow: Should be higher than Net Income.
                4. Free Cash Flow: Should be higher than Net Income.
                5. Capital Expenditures: Should be less than 25% of Net Income.
                6. Debt Management: The company should show a reduction in debt.
                7. Stock Buybacks: There should be stock repurchases.
                8. Dividends: The company should be paying dividends.
                9. Cash Balance: Should be increasing.
                
                Final Evaluation:
                Based on this analysis, provide an evaluation of the company’s cash flow strength, financial flexibility, and overall sustainability for investment. Highlight any risks or positive indicators.
                """
    
            def analyze_stock2(prompt_text, tokens):
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
            income_statement_analysis = analyze_stock2(income_statement_prompt,2000)
            balance_sheet_analysis = analyze_stock2(balance_sheet_prompt,2000)
            cashflow_statement_analysis = analyze_stock2(cashflow_statement_prompt,2000)
    
            analysis2 = {
                'income': income_statement_analysis,
                'balance' : balance_sheet_analysis,
                'cashflow' : cashflow_statement_analysis
            }
        except Exception as e:
            analysis2 = ""
        ########################

        ##### 5-Point Ratings Analysis #####
        try:
            api_key = st.secrets["GROQ_API_KEY3"]
            client = Groq(api_key=api_key)
            snowflake_prompt = f"""
                Analyze the stock {upper_ticker} and rate each category on a scale of 1 to 5 (where 1 is worst and 5 is best). Use the following financial data:
                - Historical price data: {extended_data_r}
                - Key financial metrics: 
                    - Valuation: P/E Ratio = {peRatio}, P/B Ratio = {pbRatio}, EV/EBITDA = {ev_to_ebitda}
                    - Profitability: Net profit margin = {profitmargin_pct}, ROE = {roe_value}, ROA = {roa_value}, Gross margin = {grossmargin_pct}
                    - Growth: Revenue growth = {revenue_growth_value}, Earnings growth = {earnings_growth_value}
                    - Financial health: Debt-to-equity = {deRatio_value}, Current ratio = {current_ratio}, Quick ratio = {quick_ratio}
                    - Cash flow: Free cash flow = {fcf}, Operating cash flow margin = {operatingmargin_pct}
                    - Dividends: Dividend yield = {dividendYield_value}, Dividend payout ratio = {payoutRatio}
                - Income Statement data: {income_statement_tb}
                - Balance Sheet data: {balance_sheet_tb}
                - Cashflow Statement data: {cashflow_statement_tb}
                        
                Provide ONLY these 5 numbers in the exact format below (no other text):
                stock_current_value:X
                future_performance:X
                past_performance:X
                company_health:X
                dividend:X
    
                Each rating for future_performance, past_performance, company_health and dividend must be an integer between 1 and 5, where:
                5 = Excellent
                4 = Good
                3 = Average
                2 = Below Average
                1 = Poor

                For stock_current_price_valuation, use these ratings, where:
                5 = Very Cheap
                4 = Cheap
                3 = Average
                2 = Expensive
                1 = Very Expensive
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
        ########################
    
    return (
        #Profile
        price, beta, name, sector, industry, employee, marketCap, longProfile, website, ticker, picture_url, country, sharesOutstanding, exchange_value, upper_ticker, previous_close, beta_value, sharesOutstanding_value, employee_value, marketCap_value, change_percent, change_dollar, apiKey,
    )

''
''
#############################################        #############################################
############################################# Inputs #############################################
#############################################        #############################################

main_col1, main_col2 = st.columns([3,1])
with main_col1:
    st.title("US Stock Analysis Tool (Beta)")
    input_col1, input_col2, input_col3 = st.columns([1, 3, 1])
    with input_col1:
        ticker = st.text_input("US Stock Ticker:", "AAPL")
    with input_col2:
        apiKey = st.text_input("Enter your RapidAPI Key (optional):", "")

st.write("This analysis dashboard is designed to enable beginner investors to analyze stocks effectively and with ease. Please note that the information in this page is intended for educational purposes only and it does not constitute investment advice or a recommendation to buy or sell any security. We are not responsible for any losses resulting from trading decisions based on this information.")
st.info("Certain sections require API keys to operate. Users are advised to subscribe to the Morningstar and Seeking Alpha APIs provided by Api Dojo through rapidapi.com.")

use_ai = st.checkbox("Analyze using AI (The system will use the deepseek-r1-distill-llama-70b model to analyze the stock. It will take some time for the process to complete. For a faster process, please uncheck this box.)", value=True)
""
st.caption("This tool is developed by Invest IQ Central.")
if st.button("Get Data"):
    try: 
        (
        #Profile
        price, beta, name, sector, industry, employee, marketCap, longProfile, website, ticker, picture_url, country, sharesOutstanding, exchange_value, upper_ticker, previous_close, beta_value, sharesOutstanding_value, employee_value, marketCap_value, change_percent, change_dollar, apiKey) = get_stock_data(ticker, apiKey if apiKey.strip() else None, use_ai)
    

#############################################         #############################################
############################################# Profile #############################################
#############################################         #############################################

        st.header(f'{name}', divider='gray')
        st.write(f"**Ticker:** {price}") 

    except Exception as e:
        st.write(e)
        st.error(f"Failed to fetch data. Please check your ticker again.")
        st.warning("This tool supports only tickers from the U.S. stock market. Please note that ETFs and cryptocurrencies are not available for analysis. If the entered ticker is valid but the tool does not display results, it may be due to missing data or a technical issue. Kindly try again later. If the issue persists, please contact the developer for further assistance.")
''

