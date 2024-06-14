import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

from datapipeline import historical_data, price

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

def year_backtest(metric, start_date, index):
    less_equal_zero, quintiles = rank_by(start_date, index, metric)
    portfolios = [less_equal_zero] + quintiles
    portfolio_tickers = [portfolio['TICKER'].tolist() for portfolio in portfolios]

    start_date = pd.to_datetime(start_date)
    end_date = start_date + timedelta(days=365)

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

#-----------[rebalanced_portfolio]-----------#
#                                            #
# uses year_backtest to rebalance portfolio  #
#    input metric, start date, & end date    #
#      default June 2000 ---> Dec 2023       #
#                                            #
#--------------------------------------------#

def rebalanced_portfolio(metric, index, start_date='2000-06-30', end_date='2023-12-31'):
    current_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    cumulative_portfolios = [pd.DataFrame(columns=['Date', 'Return']) for _ in range(6)]
    portfolio_stats = {i: [] for i in range(6)}

    while current_date < end_date:
        annual_returns, portfolios = year_backtest(metric, current_date.strftime('%Y-%m-%d'), index)

        for i in range(6):
            cumulative_portfolios[i] = pd.concat([cumulative_portfolios[i], annual_returns[i]]).reset_index(drop=True)
            if not portfolios[i].empty:
                stats = {
                    'Year': current_date.year,
                    'Tickers': portfolios[i]['TICKER'].tolist(),
                    'Min': portfolios[i][metric].min(),
                    'Max': portfolios[i][metric].max(),
                    'Mean': portfolios[i][metric].mean(),
                    'Std': portfolios[i][metric].std(),
                    'Annual Return': (1 + annual_returns[i]['Return']).prod() - 1
                }
                portfolio_stats[i].append(stats)

        current_date += timedelta(days=365)

    for portfolio in cumulative_portfolios:
        portfolio['Return'].fillna(0, inplace=True)

    return cumulative_portfolios, portfolio_stats
