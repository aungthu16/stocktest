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
    # if not df_latest.empty:
    #     st.subheader(f"Latest {LATEST_OBSERVATIONS} Monthly Economic Time Series Data") 
    #     st.dataframe(df_latest, use_container_width=True) 
    # else:
    #     st.error("No data could be retrieved. Please check your API key and network connection.")

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
    ai_ans1, ai_ans2 = st.columns([3,3])
    with ai_ans1:
        try:
            with st.spinner('Analyzing stock data...'):
                cleaned_text = analysis['summary'].replace('\\n', '\n').replace('\\', '')
                special_chars = ['$', '>', '<', '`', '|', '[', ']', '(', ')', '+', '{', '}', '!', '&']
                for char in special_chars:
                    cleaned_text = cleaned_text.replace(char, f"\\{char}")
                st.markdown(cleaned_text, unsafe_allow_html=True)
        except Exception as e:
            st.warning("AI analysis is currently unavailable.")

    with ai_ans2:
        delimiter = 'Economic Cycle level - '
        extracted_value = cleaned_text.split(delimiter)[-1].strip()
    
        current_stage = extracted_value.lower()
        st.write(current_stage)
        CYCLE_PHASES = [
            'moving to expansion', 'expansion', 'moving to peak',
            'peak', 'moving to contraction', 'contraction',
            'moving to trough', 'trough'
        ]
    
        try:
            current_index = CYCLE_PHASES.index(current_stage)
        except ValueError:
            st.error(f"Error: '{current_stage}' is not a recognized cycle phase.")
            st.stop()
        
        x_phase_points = np.linspace(0, 1.75 * np.pi, len(CYCLE_PHASES))
        offset = x_phase_points[3] - np.pi / 2
        x = np.linspace(0, 1.75 * np.pi, 100)
        y = np.sin(x - offset) * 1 
        x_position_for_stage = x_phase_points[current_index]
        y_position_for_stage = np.interp(x_position_for_stage, x, y)
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=x, y=y,
            mode='lines',
            line=dict(color='#4FC1E9', width=4),
            name='Economic Growth'
        ))
        fig.add_trace(go.Scatter(
            x=[x_position_for_stage],
            y=[y_position_for_stage],
            mode='markers',
            marker=dict(size=30, color='#4FC1E9', opacity=1, line=dict(width=2, color='white')),
            name='Current Position',
            hoverinfo='text',
            text=f"Stage: {current_stage.title()}"
        ))
        num_segments = len(CYCLE_PHASES)
        color_map = ['#FF4136', '#FF851B', '#FFDC00', '#2ECC40', '#3D9970', '#FFDC00', '#FF851B', '#FF4136']
        x_segment_starts = x_phase_points
        gradient_bar_y_level = -1.2
        for i in range(num_segments - 1):
            x_start = x_segment_starts[i]
            x_end = x_segment_starts[i+1]
            x_segment = np.linspace(x_start, x_end, 10)
            y_segment = np.full_like(x_segment, gradient_bar_y_level)
            fig.add_trace(go.Scatter(
                x=x_segment,
                y=y_segment,
                mode='lines',
                line=dict(color=color_map[i], width=15),
                hoverinfo='skip',
                showlegend=False
            ))
        fig.update_layout(
            title='Economic Cycle Position',
            #plot_bgcolor='black',
            xaxis=dict(
                tickmode='array',
                tickvals=x_phase_points,
                ticktext=[phase.title() for phase in CYCLE_PHASES],
                showgrid=False
            ),
            yaxis=dict(
                title='Economic Growth Level',
                showticklabels=False,
                showgrid=False,
                zeroline=True,
                zerolinecolor='white',
                zerolinewidth=2
            ),
            showlegend=False,
            height=450,
            yaxis_range=[-1.2, 1.2]
        )
        fig.add_annotation(
            x=0.8, y=1,
            xref="paper", yref="paper",
            text=f"Current Economic Cycle Stage: {current_stage.upper()}",
            showarrow=False,
            font=dict(size=18, color="#4FC1E9"),
            yanchor="middle",
            xanchor="center"
        )
        st.plotly_chart(fig, use_container_width=True)
    
except Exception as e:
    st.error(f"An error occurred: {e}")
