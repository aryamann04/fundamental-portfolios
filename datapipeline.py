import pandas as pd
from datetime import datetime, timedelta

#----------------[NASDAQ 100]----------------#
#                                            #
#    Reading and querying NASDAQ 100 data    #
#        provided by CRSP & Compustat        #
#                                            #
#--------------------------------------------#
def nasdaq_tickers_by_date(date_str):
    df = pd.read_csv('/Users/aryaman/Downloads/nasdaqconstituents.csv')

    df['from'] = pd.to_datetime(df['from'])
    df['thru'] = pd.to_datetime(df['thru'], errors='coerce')

    date = pd.to_datetime(date_str)
    filtered_df = df[(df['from'] <= date) & ((df['thru'].isna()) | (df['thru'] >= date))]

    tickers = filtered_df['co_tic'].tolist()

    return tickers

def nasdaq_data(given_date):
    ticker_list = nasdaq_tickers_by_date(given_date)
    df = pd.read_csv('/Users/aryaman/Downloads/nasdaq100historicaldata.csv')
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

# load price dataframe
historical_prices = pd.read_csv('/Users/aryaman/Downloads/nasdaqprices.csv', parse_dates=['datadate'])

def price(ticker, start_date, end_date, historical_prices=historical_prices):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    ticker_data = historical_prices[(historical_prices['tic'] == ticker) &
                                    (historical_prices['datadate'] >= start_date) &
                                    (historical_prices['datadate'] <= end_date)]

    if ticker_data.empty:
        print(f"Ticker {ticker} not found or no data available in the given date range.")
        return None

    return ticker_data[['datadate', 'prccd']].set_index('datadate').sort_index()

def get_full_nasdaq_data():
    full_df = pd.read_csv('/Users/aryaman/Downloads/nasdaq100historicaldata.csv')
    return full_df

def get_nasdaq_constituents():
    full_nasdaq = pd.read_csv('/Users/aryaman/Downloads/nasdaqconstituents.csv')
    return full_nasdaq
