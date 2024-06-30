import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

from datapipeline import sp500_tickers, price

def equal_weighted_returns(start_date, end_date):

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    current_date = start_date
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


def plot_cumulative_returns(start_date, end_date, custom_returns_df):
    sp500 = yf.download('^SPXEW', start=start_date, end=end_date, interval='1mo')
    sp500['Return'] = sp500['Adj Close'].pct_change()
    sp500['CumulativeReturn'] = (1 + sp500['Return']).cumprod()
    custom_returns_df['CumulativeReturn'] = (1 + custom_returns_df['Return']).cumprod()

    plt.figure(figsize=(14, 7))
    plt.plot(sp500.index, sp500['CumulativeReturn'], label='S&P 500')
    plt.plot(custom_returns_df['Date'], custom_returns_df['CumulativeReturn'], label='Custom Index')
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.title('Cumulative Return Comparison')
    plt.legend()
    plt.grid(True)
    plt.show()

start = '2023-01-01'
end = '2023-12-31'

large_cap_index = equal_weighted_returns(start, end)[0]
plot_cumulative_returns(start, end, large_cap_index)
