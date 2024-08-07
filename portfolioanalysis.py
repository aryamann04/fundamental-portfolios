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

    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    yearly_returns = []
    current_date = start_date

    while current_date < end_date:
        next_year_date = current_date + pd.DateOffset(years=1)
        index_data = yf.download(ticker, start=current_date, end=next_year_date)

        if not index_data.empty:
            start_price = index_data['Adj Close'].iloc[0]
            end_price = index_data['Adj Close'].iloc[-1]
            period_return = (end_price / start_price) - 1

            yearly_returns.append({
                'Year': current_date.year,
                'Period Return': period_return
            })

        current_date = next_year_date

    yearly_returns_df = pd.DataFrame(yearly_returns)
    yearly_returns_df.set_index('Year', inplace=True)

    return yearly_returns_df

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
    index_returns.index = pd.to_datetime(index_returns.index, format='%Y')

    index_data = pd.DataFrame({
        'Year': index_returns.index.year,
        'Period Return': index_returns['Period Return'].values,
        'Portfolio': index.upper()
    })

    portfolio_df = pd.concat([portfolio_df, index_data], ignore_index=True)
    portfolio_df = portfolio_df[portfolio_df['Year'] <= max_year]

    years = portfolio_df['Year'].nunique()
    cagr_df = portfolio_df.groupby('Portfolio')['Period Return'].apply(
        lambda x: (np.prod(1 + x) ** (1 / years)) - 1).reset_index()
    cagr_df.columns = ['Portfolio', 'CAGR']
    cagr_df['Portfolio'] = pd.Categorical(cagr_df['Portfolio'], categories=portfolio_categories, ordered=True)
    cagr_df = cagr_df.sort_values('Portfolio')

    print("*-------------------------------*")
    print(cagr_df.to_string(index=False))
    print("*-------------------------------*")

    heatmap_data = portfolio_df.pivot_table(index='Portfolio', columns='Year', values='Period Return', aggfunc='sum')
    heatmap_data = heatmap_data.reindex(portfolio_categories)

    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt=".2%", cmap='RdYlGn', center=0, cbar_kws={'format': '%.0f%%'},
                annot_kws={"size": 8, "rotation": 90})
    plt.title(f'Annual Returns by {metric}')
    plt.xticks(rotation=90)
    plt.show()
