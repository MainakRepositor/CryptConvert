from datetime import datetime, date, timedelta
import requests
import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

URL_BASE = "https://ftx.com/api"

def get_historical(coin, start_date, end_date, resolution = 86400):

    ''' This function extracts data from FTX API and returns a dataframe
      with information about historical prices according to the chosen crypto'''

    if coin == "EGLD" or coin == 'DOT' or coin == 'ADA':
        coin = coin + '-PERP'
    else:
        coin = coin + '/USD'

    start_time = pd.to_datetime(start_date.strftime("%Y-%m-%d")).timestamp()
    end_time = pd.to_datetime(end_date.strftime("%Y-%m-%d")).timestamp()

    url =  f'{URL_BASE}/markets/{coin}/candles?resolution={resolution}&start_time={start_time}&end_time={end_time}'
    res = requests.get(url).json()
    result = pd.DataFrame(res['result'])
    
    result['date'] = pd.to_datetime(result['time']/1000, unit = 's', origin = 'unix')
    result.drop(['startTime', 'time'], axis = 1, inplace = True)
    return result

def get_market(coin: str):

    '''This function extracts data from FTX API and returns a dataframe
    with insights according to the chosen crypto'''

    if coin == "EGLD" or coin == 'DOT' or coin == 'ADA':
        coin = coin + '-PERP'
    else:
        coin = coin + '/USD'

    url =  f'{URL_BASE}/markets/{coin}'
    res = requests.get(url).json()
    result = pd.DataFrame(res['result'], index = [0])
    priceHigh24h = float(result['priceHigh24h'])
    priceLow24h = float(result['priceLow24h'])
    volumeUsd24h = float(result['volumeUsd24h'])
    change24h = float(result['change24h'])
    price = float(result['price'])
    items = [price, priceHigh24h, priceLow24h, change24h, volumeUsd24h]
    return items

def pageII():

    st.title('Crypto Dashboard', anchor = "title")
    # Sidebar

    tickers = ('BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'MATIC', 'EGLD', 'DOGE', 'XRP', 'UNI')
    dropdown = st.sidebar.selectbox('Pick a coin from the list', tickers)
    start_date = st.sidebar.date_input('Start Date', value = pd.to_datetime('2022-07-01'), key = 'dstart_date')
    end_date = st.sidebar.date_input('End Date', value = pd.to_datetime('now'), key = 'dend_date')
    dresolution = st.sidebar.slider('Resolution', min_value = 86400, max_value = 86400*30, step = 86400, key = 'dresolution')

    # Page
    col1, col2 = st.columns([1, 5])
    coin_image = f'img/{dropdown.lower()}.png'
    col1.header(f'{dropdown}/USD')
    col2.image(coin_image, width = 60)

    coin_df = get_historical(dropdown, start_date = start_date, end_date = end_date, resolution = dresolution)

    check = st.radio('Filter', ['1D', '7D', '1M', '3M', '1Y', 'All', 'None'], horizontal = True, index = 6)

    if check == '1D':
        back_days = date.today() - timedelta(days = 1)
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        resolution = st.select_slider('Resolution', options = [15, 60, 300, 900, 3600, 14400, 86400], key = '1dresolution')
        coin_df = get_historical(dropdown, start_date = start_date, end_date = end_date, resolution = resolution)

    if check == '7D':
        back_days = date.today() - timedelta(days = 7)
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        coin_df = get_historical(dropdown, start_date = start_date, end_date = end_date, resolution = 900)
        resolution = st.select_slider('Resolution', options = [300, 900, 3600, 14400, 86400, 86400*2, 86400*3], key = '7dresolution')
        coin_df = get_historical(dropdown, start_date = start_date, end_date = end_date, resolution = resolution)

    if check == '1M':
        back_days = date.today() - timedelta(days = 30)
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        resolution = st.select_slider('Resolution', options = [900, 3600, 14400, 86400, 86400*2, 86400*3, 86400*4], key = '1mresolution')
        coin_df = get_historical(dropdown, start_date = start_date, end_date = end_date, resolution = resolution)

    if check == '3M':
        back_days = date.today() - timedelta(days = 90)
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        resolution = st.select_slider('Resolution', options = [3600, 14400, 86400, 86400*2, 86400*3, 86400*4, 86400*7], key = '3mresolution')
        coin_df = get_historical(dropdown, start_date = start_date, end_date = end_date, resolution = resolution)

    if check == '1Y':
        back_days = date.today() - timedelta(days = 365)
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        resolution = st.select_slider('Resolution', options = [86400, 86400*5, 86400*10, 86400*15, 86400*20, 86400*25, 86400*30], key = '1yresolution')
        coin_df = get_historical(dropdown, start_date = start_date, end_date = end_date, resolution = resolution)

    if check == 'All':
        back_days = date.today() - timedelta(days = 1095) # 3 years
        start_date = pd.to_datetime(back_days)
        end_date = pd.to_datetime('now')
        resolution = st.select_slider('Resolution', options = [86400, 86400*5, 86400*10, 86400*15, 86400*20, 86400*25, 86400*30], key = '1yresolution')
        coin_df = get_historical(dropdown, start_date = start_date, end_date = end_date, resolution = resolution)

    if check == 'None':
        pass

    # Moving average - 30weeks
    coin_df['30wma'] = coin_df['close'].rolling(30).mean()
    variance = round(np.var(coin_df['close']),3)
    items = get_market(dropdown)
    price = items[0]
    priceHigh24h = items[1]
    priceLow24h = items[2]
    change24h = items[3]
    volumeUsd24h = items[4]

    col1, col2, col3, col4 = st.columns([2, 2, 2, 8])
    col1.metric('Price', f'{price:,}', f'{round(change24h*100,2)}%')
    col2.metric('24h High', f'{priceHigh24h:,}')
    col3.metric('24h Low', f'{priceLow24h:,}')
    col4.metric('24h Volume', f'{volumeUsd24h:,}')

    st.metric('Variance', f'{variance:,}')

    # Candle and volume chart
    fig = make_subplots(rows = 2, cols = 1, shared_xaxes = True, vertical_spacing = 0.1, row_heights = [100,30])
    fig.add_trace(
        go.Candlestick(x = coin_df['date'],
                        open = coin_df['open'], high = coin_df['high'],
                        low = coin_df['low'], close = coin_df['close'],
                        name = 'Candlestick',
                        ), row = 1, col = 1
    )

    fig.update_layout(xaxis_rangeslider_visible = False)

    fig.add_trace(
        go.Scatter(
            x = coin_df['date'],
            y = coin_df['30wma'],
            line = dict(color = '#e0e0e0', width = 2, dash = 'dot'),
            name = "30-week MA"
        ), row = 1, col = 1
    )

    # Bar chart https://plotly.com/python-api-reference/generated/plotly.graph_objects.bar.html#plotly.graph_objects.bar.Marker
    fig.add_trace(
        go.Bar(
            x = coin_df['date'],
            y = coin_df['volume'],
            marker = dict(color = coin_df['volume'], colorscale = 'aggrnyl_r'),
            name = 'Volume'
        ), row = 2, col = 1
    )
    fig['layout']['xaxis2']['title'] = 'Date'
    fig['layout']['yaxis']['title'] = 'Price'
    fig['layout']['yaxis2']['title'] = 'Volume'
    st.plotly_chart(fig, use_container_width = True)

    # Show data
    if st.checkbox('Show data'):
        st.dataframe(coin_df)