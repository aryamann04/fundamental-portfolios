import yfinance as yf
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

def index_return(index, start_date, end_date):
    if index == 'nasdaq100':
        ticker = '^IXIC'
    else:
        ticker = '^GSPC'

    index_data = yf.download(ticker, start=start_date, end=end_date)
    index_returns = index_data['Adj Close'].pct_change().dropna()

    rolling_yearly_returns = (1 + index_returns).rolling(252).apply(np.prod, raw=True) - 1
    rolling_yearly_df = pd.DataFrame(rolling_yearly_returns, columns=['Period Return'])
    rolling_yearly_df.index = pd.to_datetime(rolling_yearly_df.index)

    return rolling_yearly_df.dropna()

def portfolio_analysis(portfolio_stats, metric, index):
    portfolio_categories = ['<=0', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', index.upper()]

    all_data = []
    for portfolio, stats_list in portfolio_stats.items():
        for stats in stats_list:
            stats['Portfolio'] = portfolio_categories[portfolio]
            stats['Period Return'] = stats['Period Return']
            all_data.append(stats)

    portfolio_df = pd.DataFrame(all_data)

    min_year = portfolio_df['Year'].min()
    min_month = portfolio_df.loc[portfolio_df['Year'] == min_year, 'Month'].min()
    max_year = portfolio_df['Year'].max()
    max_month = portfolio_df.loc[portfolio_df['Year'] == max_year, 'Month'].max()

    start_date = f"{min_year}-{min_month:02d}-01"
    end_date = f"{max_year + 1}-{max_month:02d}-01"
    index_returns = index_return(index, start_date, end_date)

    index_returns_filtered = index_returns[index_returns.index.month == min_month]
    index_returns_filtered = index_returns_filtered[index_returns_filtered.index.year >= min_year + 1]

    index_data = pd.DataFrame({
        'Year': index_returns_filtered.index.year,
        'Month': index_returns_filtered.index.month,
        'Period Return': index_returns_filtered['Period Return'].values,
        'Portfolio': index.upper()
    })

    portfolio_df = pd.concat([portfolio_df, index_data], ignore_index=True)

    years = portfolio_df['Year'].nunique()
    cagr_df = portfolio_df.groupby('Portfolio')['Period Return'].apply(
        lambda x: (np.prod(1 + x) ** (1 / years)) - 1).reset_index()
    cagr_df.columns = ['Portfolio', 'CAGR']
    cagr_df['Portfolio'] = pd.Categorical(cagr_df['Portfolio'], categories=portfolio_categories, ordered=True)
    cagr_df = cagr_df.sort_values('Portfolio')

    print("Compounded Annual Growth Rates (CAGR) for each Portfolio:")
    print(cagr_df.to_string(index=False))

    heatmap_data = portfolio_df.pivot_table(index='Portfolio', columns='Year', values='Period Return', aggfunc='sum')
    heatmap_data = heatmap_data.reindex(portfolio_categories)

    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".2%", cmap='RdYlGn', center=0, cbar_kws={'format': '%.0f%%'},
                annot_kws={"size": 8, "rotation": 90})
    plt.title(f'Annual Returns by {metric}')
    plt.xticks(rotation=90)
    plt.show()
