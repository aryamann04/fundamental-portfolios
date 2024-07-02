import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

largecap_tickers = pd.read_csv('/Users/aryaman/Downloads/sp500historicalconstituents.csv', parse_dates=['date'])

def all_largecap_tickers():
    tickers = set()
    for tickers_list in largecap_tickers['tickers']:
        tickers.update(tickers_list.strip("[]").replace("'", "").split(", "))
    return list(tickers)

def read_and_process_csv():
    df = pd.read_csv('/Users/aryaman/Downloads/sp500monthlyreturn.csv')
    df['date'] = pd.to_datetime(df['MthCalDt']).dt.to_period('M')
    return df

def largecap_tickers(date):
    df = pd.read_csv('/Users/aryaman/Downloads/sp500historicalconstituents.csv')
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m').dt.to_period('M')

    closest_date = df[df['date'] <= date]['date'].max()
    tickers = df[df['date'] == closest_date]['tickers'].values[0]
    tickers_list = tickers.strip("[]").replace("'", "").split(", ")

    return tickers_list

def mcap_dataframes():
    df = read_and_process_csv()
    date_range = pd.period_range(start='2008-01', end='2023-12', freq='M')

    mkt_cap = pd.DataFrame(index=date_range)
    mth_return = pd.DataFrame(index=date_range)
    mcap_weights = pd.DataFrame(index=date_range)
    mcap_weighted_return = pd.DataFrame(index=date_range)

    for date in date_range:
        print(f"Processing date: {date}")

        tickers = largecap_tickers(date)
        df_filtered = df[df['date'] == date]

        for ticker in tickers:
            ticker_data = df_filtered[df_filtered['Ticker'] == ticker]
            if not ticker_data.empty:
                mkt_cap.at[date, ticker] = ticker_data['MthCap'].values[0]
                mth_return.at[date, ticker] = ticker_data['MthRetx'].values[0]

        if date in mkt_cap.index:
            total_market_cap = mkt_cap.loc[date].sum()
            if total_market_cap != 0:
                for ticker in tickers:
                    if ticker in mkt_cap.columns:
                        mcap_weights.at[date, ticker] = mkt_cap.at[date, ticker] / total_market_cap

        if date in mcap_weights.index:
            row_sum = mcap_weights.loc[date].sum()
            if row_sum != 0:
                mcap_weights.loc[date, 'SumOfWeights'] = row_sum
                mcap_weights.loc[date] = mcap_weights.loc[date] / row_sum

    mcap_weighted_return = mth_return * mcap_weights
    portfolio_return = mcap_weighted_return.sum(axis=1)
    mcap_index = pd.DataFrame({'date': date_range.astype(str), 'return': portfolio_return})

    mkt_cap['n'] = mkt_cap.notna().sum(axis=1)
    mth_return['n'] = mth_return.notna().sum(axis=1)
    mcap_weights['n'] = mcap_weights.notna().sum(axis=1)
    mcap_weighted_return['n'] = mcap_weighted_return.notna().sum(axis=1)
    mcap_index['n'] = mcap_weighted_return['n']

    # equal weight index
    mth_return['EqualWeightReturn'] = mth_return.apply(lambda row: row.dropna().mean(), axis=1)
    eqw_index = pd.DataFrame({'date': date_range.astype(str), 'return': mth_return['EqualWeightReturn'] - 1})
    eqw_index['n'] = mcap_weighted_return['n']

    # check if weights sum to 1
    print(f"All weights sum to 1: {all(abs(mcap_weights['SumOfWeights'] - 1) < 1e-6)}")

    return mkt_cap, mth_return, mcap_weights, mcap_weighted_return, mcap_index, eqw_index

def plot_return(final_df, equal_weight=False):
    start_date = '2008-01-01'
    end_date = '2023-12-31'

    if equal_weight:
        sp500 = yf.download('^SPXEW', start=start_date, end=end_date, interval='1mo', progress=False)
    else:
        sp500 = yf.download('^SPX', start=start_date, end=end_date, interval='1mo', progress=False)

    sp500['Return'] = sp500['Adj Close'].pct_change()
    sp500['CumulativeReturn'] = (1 + sp500['Return']).cumprod()

    final_df['date'] = pd.to_datetime(final_df['date'])
    final_df.set_index('date', inplace=True)
    final_df['CumulativeReturn'] = (1 + final_df['return']).cumprod()

    plt.figure(figsize=(14, 7))

    if equal_weight:
        plt.plot(sp500.index, sp500['CumulativeReturn'], label='S&P 500 Equal Weight')
        plt.plot(final_df.index, final_df['CumulativeReturn'], label='Large Cap Equal Weight')
        plt.title('Cumulative Return Comparison: Large Cap Equal Weight Index vs S&P 500 Equal Weight')
    else:
        plt.plot(sp500.index, sp500['CumulativeReturn'], label='S&P 500')
        plt.plot(final_df.index, final_df['CumulativeReturn'], label='Large Cap Market Cap Weight')
        plt.title('Cumulative Return Comparison: Large Cap Market Cap Weight Index vs S&P 500')

    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.legend()
    plt.grid(True)
    plt.show()

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

_, _, _, _, mcap_index, eqw_index = mcap_dataframes()

plot_return(eqw_index, equal_weight=True)
plot_return(mcap_index, equal_weight=False)
