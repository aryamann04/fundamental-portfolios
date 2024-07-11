import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf

from datetime import datetime, timedelta
from datapipeline import historical_data, price
from largecapindex import process_csv
#------------------[rank_by]-----------------#
#                                            #
#     ranks index constituents by a given    #
#  metric into quintiles as of a given date  #
#         input given_date & metric          #
#                                            #
#--------------------------------------------#

def rank_by(given_date, index, metric, **kwargs):
    df = historical_data(given_date, index)
    metrics = ['CAPEI', 'bm', 'evm', 'pe_op_basic', 'pe_op_dil', 'pe_exi', 'pe_inc', 'ps', 'pcf', 'dpr', 'npm',
               'opmbd', 'opmad', 'gpm', 'ptpm', 'cfm', 'roa', 'roe', 'roce', 'efftax', 'aftret_eq', 'aftret_invcapx',
               'aftret_equity', 'pretret_noa', 'pretret_earnat', 'GProf', 'equity_invcap', 'debt_invcap',
               'totdebt_invcap', 'capital_ratio', 'int_debt', 'int_totdebt', 'cash_lt', 'invt_act', 'rect_act',
               'debt_at', 'debt_ebitda', 'short_debt', 'curr_debt', 'lt_debt', 'profit_lct', 'ocf_lct', 'cash_debt',
               'fcf_ocf', 'lt_ppent', 'dltt_be', 'debt_assets', 'debt_capital', 'de_ratio', 'intcov', 'intcov_ratio',
               'cash_ratio', 'quick_ratio', 'curr_ratio', 'cash_conversion', 'inv_turn', 'at_turn', 'rect_turn',
               'pay_turn', 'sale_invcap', 'sale_equity', 'sale_nwc', 'rd_sale', 'adv_sale', 'staff_sale', 'accrual',
               'ptb', 'PEG_trailing', 'divyield']

    assert metric in metrics, f"Invalid metric. Choose one of: {', '.join(metrics)}"
    assert metric in df.columns, f"Metric '{metric}' not found in the dataframe columns."

    df = df.sort_values(by=metric).reset_index(drop=True)
    less_equal_zero = df[df[metric] <= 0]
    quintiles = pd.qcut(df[df[metric] > 0][metric], 5, labels=False)

    quintile_groups = []
    for i in range(5):
        quintile_groups.append(df[df[metric] > 0][quintiles == i])

    return less_equal_zero, quintile_groups

#---------------[year_backtest]--------------#
#                                            #
#  uses rank_by and CRSP data to calculate   #
#  returns for all quintiles in a given year #
#         input metric & start_date          #
#                                            #
#--------------------------------------------#

def backtest(metric, start_date, index, frequency='yearly'):
    # Rank portfolios based on the given metric
    less_equal_zero, quintiles = rank_by(start_date, index, metric)
    portfolios = [less_equal_zero] + quintiles
    portfolio_tickers = [portfolio['TICKER'].tolist() for portfolio in portfolios]

    # Convert start_date to datetime and set the end_date based on the frequency
    start_date = pd.to_datetime(start_date)
    if frequency == 'monthly':
        end_date = start_date + pd.DateOffset(months=1)
    elif frequency == 'quarterly':
        end_date = start_date + pd.DateOffset(months=3)
    elif frequency == 'yearly':
        end_date = start_date + timedelta(days=365)
    else:
        raise ValueError("Invalid frequency. Choose from 'monthly', 'quarterly', or 'yearly'.")

    daily_returns_list = []

    for tickers in portfolio_tickers:
        if not tickers:
            daily_returns_list.append(pd.DataFrame(columns=['Date', 'Return']))
            continue

        price_data = pd.DataFrame()

        for ticker in tickers:
            ticker_data = price(ticker, start_date, end_date, index)
            if ticker_data is not None:
                price_data[ticker] = ticker_data['prccd']

        if not price_data.empty:
            daily_returns = price_data.pct_change().mean(axis=1)
            daily_returns_df = daily_returns.reset_index()
            daily_returns_df.columns = ['Date', 'Return']
            daily_returns_list.append(daily_returns_df)
        else:
            daily_returns_list.append(pd.DataFrame(columns=['Date', 'Return']))

    return daily_returns_list, portfolios

def mcap_backtest(metric, start_date, index='sp500'):
    less_equal_zero, quintiles = rank_by(start_date, index, metric)
    portfolios = [less_equal_zero] + quintiles
    portfolio_tickers = [portfolio['TICKER'].tolist() for portfolio in portfolios]

    df = process_csv()

    start_date = pd.to_datetime(start_date)
    end_date = start_date + pd.DateOffset(months=1)
    date_range = pd.period_range(start=start_date, end=end_date, freq='M')
    portfolio_dfs = []

    for portfolio in portfolio_tickers:

        mkt_cap = pd.DataFrame(index=date_range)
        mth_return = pd.DataFrame(index=date_range)
        mcap_weights = pd.DataFrame(index=date_range)
        mcap_weighted_return = pd.DataFrame(index=date_range)

        for date in date_range:
            tickers = portfolio
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
        portfolio_df = pd.DataFrame({'Date': pd.to_datetime(date_range.astype(str)), 'Return': portfolio_return})
        portfolio_dfs.append(portfolio_df)

    return portfolio_dfs, portfolios

#-----------[rebalanced_portfolio]-----------#
#                                            #
#    uses backtest to rebalance portfolio    #
#    input metric, start date, & end date    #
#      default June 2000 ---> Dec 2023       #
#                                            #
#--------------------------------------------#

def rebalanced_portfolio(metric, index, start_date='2000-06-30', end_date='2023-12-31', frequency='yearly', mcap=False):
    if mcap:
        frequency = 'monthly'
    current_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    cumulative_portfolios = [pd.DataFrame(columns=['Date', 'Return']) for _ in range(6)]
    portfolio_stats = {i: [] for i in range(6)}

    while current_date < end_date:
        if mcap:
            returns, portfolios = mcap_backtest(metric, current_date.strftime('%Y-%m-%d'), index)
        else:
            returns, portfolios = backtest(metric, current_date.strftime('%Y-%m-%d'), index)

        for i in range(6):
            cumulative_portfolios[i] = pd.concat([cumulative_portfolios[i], returns[i]]).reset_index(drop=True)
            if not portfolios[i].empty:
                stats = {
                    'Year': current_date.year,
                    'Tickers': portfolios[i]['TICKER'].tolist(),
                    'Min': portfolios[i][metric].min(),
                    'Max': portfolios[i][metric].max(),
                    'Mean': portfolios[i][metric].mean(),
                    'Std': portfolios[i][metric].std(),
                    'Annual Return': (1 + returns[i]['Return']).prod() - 1
                }
                portfolio_stats[i].append(stats)

        if frequency == 'monthly':
            current_date += pd.DateOffset(months=1)
        elif frequency == 'quarterly':
            current_date += pd.DateOffset(months=3)
        else:
            current_date += timedelta(days=365)

    for portfolio in cumulative_portfolios:
        portfolio['Return'].fillna(0, inplace=True)

    return cumulative_portfolios, portfolio_stats
