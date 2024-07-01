import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime, timedelta
from datapipeline import sp500_tickers, price

largecap_tickers = pd.read_csv('/Users/aryaman/Downloads/sp500historicalconstituents.csv', parse_dates=['date'])

def all_largecap_tickers():
    tickers = set()
    for tickers_list in largecap_tickers['tickers']:
        tickers.update(tickers_list.strip("[]").replace("'", "").split(", "))
    return list(tickers)

def equal_weighted_returns(start_date, end_date):

    current_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    daily_returns_list = []

    while current_date <= end_date:
        # Get the tickers for the current month
        tickers = sp500_tickers(current_date)
        price_data = pd.DataFrame()

        for ticker in tickers:
            ticker_data = price(ticker, start_date, end_date, 'sp500')
            if ticker_data is not None:
                price_data[ticker] = ticker_data['prccd']

        if not price_data.empty:
            daily_returns = price_data.pct_change().mean(axis=1)
            daily_returns_df = daily_returns.reset_index()
            daily_returns_df.columns = ['Date', 'Return']
            daily_returns_list.append(daily_returns_df)
        else:
            daily_returns_list.append(pd.DataFrame(columns=['Date', 'Return']))

        # Move to the next month
        current_date += pd.DateOffset(months=1)

    return daily_returns_list

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

def create_price_dataframe():
    df = read_and_process_csv()

    # Define the date range
    date_range = pd.period_range(start='1987-07', end='2023-12', freq='M')

    # Initialize the dataframes
    mkt_cap = pd.DataFrame(index=date_range)
    mth_return = pd.DataFrame(index=date_range)
    mcap_weights = pd.DataFrame(index=date_range)
    mcap_weighted_return = pd.DataFrame(index=date_range)

    # Iterate over each date in the date range
    for date in date_range:
        print(f"Processing date: {date}")
        tickers = largecap_tickers(date)

        # Filter the data for the current date
        df_filtered = df[df['date'] == date]

        # Populate mkt_cap and mth_return dataframes
        for ticker in tickers:
            ticker_data = df_filtered[df_filtered['Ticker'] == ticker]
            if not ticker_data.empty:
                mkt_cap.at[date, ticker] = ticker_data['MthCap'].values[0]
                mth_return.at[date, ticker] = ticker_data['MthRetx'].values[0]

        # Calculate market cap weights
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

    # Calculate market cap weighted return
    mcap_weighted_return = mth_return * mcap_weights
    portfolio_return = mcap_weighted_return.sum(axis=1)

    # Create the final dataframe with date and return
    final_df = pd.DataFrame({'date': date_range.astype(str), 'return': portfolio_return})

    all_rows_sum_to_1 = all(abs(mcap_weights.sum(axis=1) - 1) < 1e-6)
    print(f"All rows in mcap_weights sum to 1: {all_rows_sum_to_1}")
    all_rows_sum_to_1 = all(abs(mcap_weights.sum(axis=1) - 1) < 1e-6)
    if not all_rows_sum_to_1:
        # Print rows where sum of weights is not equal to 1
        print("Rows where sum of weights is not equal to 1:")
        print(mcap_weights[abs(mcap_weights.sum(axis=1) - 1) >= 1e-6])

    return mkt_cap, mth_return, mcap_weights, mcap_weighted_return, final_df

def plot_return(final_df):
    # Define start and end dates
    start_date = '1987-07-01'
    end_date = '2023-12-31'

    # Download S&P 500 data using yfinance with monthly frequency
    sp500 = yf.download('^GSPC', start=start_date, end=end_date, interval='1mo', progress=False)
    sp500['Return'] = sp500['Adj Close'].pct_change()
    sp500['CumulativeReturn'] = (1 + sp500['Return']).cumprod()

    # Convert 'date' column in final_df to datetime if needed
    final_df['date'] = pd.to_datetime(final_df['date'])
    final_df.set_index('date', inplace=True)

    # Calculate cumulative return for custom index
    final_df['CumulativeReturn'] = (1 + final_df['return']).cumprod()

    # Plotting
    plt.figure(figsize=(14, 7))
    plt.plot(sp500.index, sp500['CumulativeReturn'], label='S&P 500')
    plt.plot(final_df.index, final_df['CumulativeReturn'], label='Custom Index')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.title('Cumulative Return Comparison: Custom Index vs S&P 500')
    plt.legend()
    plt.grid(True)
    plt.show()

# Example usage:
mkt_cap, mth_return, mcap_weights, mcap_weighted_return, final_df = create_price_dataframe()
plot_return(final_df)
