import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf
import matplotlib.colors as mcolors
import numpy as np

def plot_portfolio_returns(daily_returns_list, start_date, end_date, granularity, index):
    if not daily_returns_list or not isinstance(daily_returns_list, list):
        print("Input should be a list of DataFrames with daily returns.")
        return

    portfolio_names = ['Less than or equal to 0', 'Quintile 1', 'Quintile 2', 'Quintile 3', 'Quintile 4', 'Quintile 5']
    num_portfolios = len(daily_returns_list)
    colors = plt.cm.Blues(np.linspace(0.3, 1, num_portfolios))  # Generate shades of blue

    for df in daily_returns_list:
        if not df.empty:
            date_range = df['Date']
            break
    else:
        print("No non-empty dataframes found in daily_returns_list.")
        return

    if index == 'nasdaq100':
        if granularity == 'daily':
            index_return = yf.download('^NDX', start=start_date, end=end_date)
        else:
            index_return = yf.download('^NDX', start=start_date, end=end_date, interval='3mo')
    elif index == 'russell200':
        if granularity == 'daily':
            index_return = yf.download('^RUT', start=start_date, end=end_date)
        else:
            index_return = yf.download('^RUT', start=start_date, end=end_date, interval='3mo')

    index_return['Return'] = index_return['Adj Close'].pct_change()
    index_return['Cumulative Return'] = (1 + index_return['Return']).cumprod()
    index_return['Cumulative Return'] = (1 + index_return['Return']).cumprod()

    plt.figure(figsize=(12, 8))

    for i, daily_returns_df in enumerate(daily_returns_list):
        if daily_returns_df.empty:
            continue
        daily_returns_df = resample_data(daily_returns_df, granularity)
        daily_returns_df['Cumulative Return'] = (1 + daily_returns_df['Return']).cumprod()
        plt.plot(daily_returns_df['Date'], daily_returns_df['Cumulative Return'], label=portfolio_names[i], color=colors[i])

    if index == 'nasdaq100':
        plt.plot(index_return.index, index_return['Cumulative Return'], label='NASDAQ 100', linestyle='--', color='black')
    elif index == 'russell200':
        plt.plot(index_return.index, index_return['Cumulative Return'], label='Russell 2000', linestyle='--', color='black')

    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.title('Portfolio Cumulative Returns Over Time')
    plt.legend()
    plt.grid(True)
    plt.show()

def print_portfolio_stats(portfolio_stats):
    for i, stats in portfolio_stats.items():
        print(f"\nPortfolio {i}:")
        for stat in stats:
            print(stat)

def resample_data(df, granularity):
    if 'Date' not in df.columns:
        raise KeyError("The DataFrame does not have a 'Date' column.")

    df = df.set_index('Date')

    if granularity == 'quarterly':
        df_resampled = df.resample('Q').agg({'Return': lambda x: (1 + x).prod() - 1})
    elif granularity == 'yearly':
        df_resampled = df.resample('Y').agg({'Return': lambda x: (1 + x).prod() - 1})
    else:  # default to daily
        df_resampled = df

    df_resampled = df_resampled.reset_index()
    return df_resampled
