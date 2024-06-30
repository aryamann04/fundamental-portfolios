import pandas as pd
from datetime import datetime, timedelta

#----------------[NASDAQ 100]----------------#
#                                            #
#    Reading and querying NASDAQ 100 data    #
#        provided by CRSP & Compustat        #
#                                            #
#--------------------------------------------#
#----------------[Russell 200]---------------#
#                                            #
#   Reading and querying Russell 200 data    #
#        provided by CRSP & Compustat        #
#                                            #
#--------------------------------------------#

def nasdaq_tickers(date):
    df = pd.read_csv('/Users/aryaman/Downloads/nasdaqconstituents.csv')
    df['from'] = pd.to_datetime(df['from'])
    df['thru'] = pd.to_datetime(df['thru'], errors='coerce')

    date = pd.to_datetime(date)
    filtered_df = df[(df['from'] <= date) & ((df['thru'].isna()) | (df['thru'] >= date))]
    tickers = filtered_df['co_tic'].tolist()

    return tickers

def russell200_tickers(date):
    russell_data = pd.read_csv('/Users/aryaman/Downloads/russell200constituents.csv', parse_dates=['Date'])
    date = pd.to_datetime(date)
    filtered_data = russell_data[russell_data['Date'] <= date]
    if filtered_data.empty:
        return []

    most_recent_date = filtered_data['Date'].max()
    data = filtered_data[filtered_data['Date'] == most_recent_date]
    return data['Ticker'].unique().tolist()

def sp500_tickers(date):
    date = pd.to_datetime(date).to_period('M')
    df = pd.read_csv('/Users/aryaman/Downloads/sp500historicalconstituents.csv')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m').dt.to_period('M')

    closest_date = df[df['date'] <= date]['date'].max()
    tickers = df[df['date'] == closest_date]['tickers'].values[0]
    tickers_list = tickers.strip("[]").replace("'", "").split(", ")

    return tickers_list

def historical_data(given_date, index):
    if index == 'nasdaq100':
        ticker_list = nasdaq_tickers(given_date)
        df = pd.read_csv('/Users/aryaman/Downloads/nasdaq100historicaldata.csv')
    elif index == 'russell200':
        ticker_list = russell200_tickers(given_date)
        df = pd.read_csv('/Users/aryaman/Downloads/russell200historicaldata.csv')
    elif index == 'sp500':
        ticker_list = sp500_tickers(given_date)
        df = pd.read_csv('/Users/aryaman/Downloads/sp500historicaldata.csv')
    else:
        raise ValueError("Invalid index.")

    df['public_date'] = pd.to_datetime(df['public_date'])
    df_filtered = df[df['TICKER'].isin(ticker_list)]
    given_date = pd.to_datetime(given_date)
    most_recent_rows = []

    for ticker in ticker_list:
        ticker_data = df_filtered[df_filtered['TICKER'] == ticker]
        recent_data = ticker_data[ticker_data['public_date'] <= given_date].sort_values(by='public_date',
                                                                                        ascending=False).head(1)
        if not recent_data.empty:
            most_recent_rows.append(recent_data)

    most_recent_df = pd.concat(most_recent_rows)
    return most_recent_df


# Load price dataframes
nasdaq_prices = pd.read_csv('/Users/aryaman/Downloads/nasdaqprices.csv', parse_dates=['datadate'])
russell_prices = pd.read_csv('/Users/aryaman/Downloads/russell200prices.csv', parse_dates=['datadate'])
sp500_prices = pd.read_csv('/Users/aryaman/Downloads/sp500prices.csv',
                             parse_dates=['datadate'])

def price(ticker, start_date, end_date, index):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    if index == 'nasdaq100':
        historical_prices = nasdaq_prices
    elif index == 'russell200':
        historical_prices = russell_prices
    elif index == 'sp500':
        historical_prices = sp500_prices
    else:
        raise ValueError("Invalid index. Use 'nasdaq100' or 'russell200'.")

    ticker_data = historical_prices[(historical_prices['tic'] == ticker) &
                                    (historical_prices['datadate'] >= start_date) &
                                    (historical_prices['datadate'] <= end_date)]

    if ticker_data.empty:
        print(f"Ticker {ticker} not found or no data available in the given date range.")
        return None

    return ticker_data[['datadate', 'prccd']].set_index('datadate').sort_index()
