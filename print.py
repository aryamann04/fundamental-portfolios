import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

import matplotlib.colors as mcolors
import matplotlib.pyplot as plt

from largecapindex import mcap_dataframes

def plot_portfolio_returns(daily_returns_list, start_date, end_date, granularity, index, metric):

    portfolio_names = ['Less than or equal to 0', 'Quintile 1', 'Quintile 2', 'Quintile 3', 'Quintile 4', 'Quintile 5']
    num_portfolios = len(daily_returns_list)
    colors = plt.cm.Blues(np.linspace(0.3, 1, num_portfolios))  # Generate shades of blue

    if index == 'nasdaq100':
        i = '^NDX'
    elif index == 'russell200':
        i = '^RUT'
    else:
        i = '^SPX'

    if granularity == 'daily':
        index_return = yf.download(i, start=start_date, end=end_date)
    else:
        index_return = yf.download(i, start=start_date, end=end_date, interval='1mo')

    index_return['Return'] = index_return['Adj Close'].pct_change()
    index_return['Cumulative Return'] = (1 + index_return['Return']).cumprod()

    plt.figure(figsize=(12, 8))

    for i, daily_returns_df in enumerate(daily_returns_list):
        if daily_returns_df.empty:
            continue
        daily_returns_df = resample_data(daily_returns_df, granularity)
        daily_returns_df['Cumulative Return'] = (1 + daily_returns_df['Return']).cumprod()
        plt.plot(daily_returns_df['Date'], daily_returns_df['Cumulative Return'], label=portfolio_names[i], color=colors[i])

    # plot calculated large cap index
    if index == 'sp500':
        start = (datetime.strptime(start_date, '%Y-%m-%d')).strftime('%Y-%m')
        end = (datetime.strptime(end_date, '%Y-%m-%d')).strftime('%Y-%m')
        _, _, _, _, mcap_index, _, = mcap_dataframes(start, end)

        mcap_index['date'] = pd.to_datetime(mcap_index['date'])
        mcap_index.set_index('date', inplace=True)
        mcap_index['CumulativeReturn'] = (1 + mcap_index['return']).cumprod()
        plt.plot(mcap_index.index, mcap_index['CumulativeReturn'], label='Large Cap Market Cap Weight', linestyle='--', color='red')

    plt.plot(index_return.index, index_return['Cumulative Return'], label=index.upper(), linestyle='--', color='black')
    plt.gca().set_xlim(right=pd.to_datetime(end_date))
    plt.xlabel('Date')
    plt.ylabel('Cumulative Return')
    plt.title(f'Portfolios by {get_metric_description(metric)} (Cumulative Returns) from {start_date} to {end_date}')
    plt.legend()
    plt.grid(True)
    plt.show()

def print_portfolio_stats(portfolio_stats):
    for i, stats in portfolio_stats.items():
        print(f"\nPortfolio {i}:")
        for stat in stats:
            print(stat)

def resample_data(df, granularity):

    df = df.set_index('Date')

    if granularity == 'quarterly':
        df_resampled = df.resample('Q').agg({'Return': lambda x: (1 + x).prod() - 1})
    elif granularity == 'yearly':
        df_resampled = df.resample('Y').agg({'Return': lambda x: (1 + x).prod() - 1})
    else:  # default to daily
        df_resampled = df

    df_resampled = df_resampled.reset_index()
    return df_resampled

def get_metric_description(metric_key):
    metrics = {
        'dpr': 'Dividend Payout Ratio',
        'PEG_trailing': 'Trailing P/E to Growth (PEG) ratio',
        'bm': 'Book/Market',
        'CAPEI': 'Shillers Cyclically Adjusted P/E Ratio',
        'divyield': 'Dividend Yield',
        'evm': 'Enterprise Value Multiple',
        'pcf': 'Price/Cash flow',
        'pe_exi': 'P/E (Diluted, Excl. EI)',
        'pe_inc': 'P/E (Diluted, Incl. EI)',
        'pe_op_basic': 'Price/Operating Earnings (Basic, Excl. EI)',
        'pe_op_dil': 'Price/Operating Earnings (Diluted, Excl. EI)',
        'ps': 'Price/Sales',
        'ptb': 'Price/Book',
        'efftax': 'Effective Tax Rate',
        'gprof': 'Gross Profit/Total Assets',
        'aftret_eq': 'After-tax Return on Average Common Equity',
        'aftret_equity': 'After-tax Return on Total Stockholders Equity',
        'aftret_invcapx': 'After-tax Return on Invested Capital',
        'gpm': 'Gross Profit Margin',
        'npm': 'Net Profit Margin',
        'opmad': 'Operating Profit Margin After Depreciation',
        'opmbd': 'Operating Profit Margin Before Depreciation',
        'pretret_earnat': 'Pre-tax Return on Total Earning Assets',
        'pretret_noa': 'Pre-tax return on Net Operating Assets',
        'ptpm': 'Pre-tax Profit Margin',
        'roa': 'Return on Assets',
        'roce': 'Return on Capital Employed',
        'roe': 'Return on Equity',
        'capital_ratio': 'Capitalization Ratio',
        'equity_invcap': 'Common Equity/Invested Capital',
        'debt_invcap': 'Long-term Debt/Invested Capital',
        'totdebt_invcap': 'Total Debt/Invested Capital',
        'invt_act': 'Inventory/Current Assets',
        'rect_act': 'Receivables/Current Assets',
        'fcf_ocf': 'Free Cash Flow/Operating Cash Flow',
        'ocf_lct': 'Operating CF/Current Liabilities',
        'cash_debt': 'Cash Flow/Total Debt',
        'cash_lt': 'Cash Balance/Total Liabilities',
        'cfm': 'Cash Flow Margin',
        'short_debt': 'Short-Term Debt/Total Debt',
        'profit_lct': 'Profit Before Depreciation/Current Liabilities',
        'curr_debt': 'Current Liabilities/Total Liabilities',
        'debt_ebitda': 'Total Debt/EBITDA',
        'dltt_be': 'Long-term Debt/Book Equity',
        'int_debt': 'Interest/Average Long-term Debt',
        'int_totdebt': 'Interest/Average Total Debt',
        'lt_debt': 'Long-term Debt/Total Liabilities',
        'lt_ppent': 'Total Liabilities/Total Tangible Assets',
        'de_ratio': 'Total Debt/Equity',
        'debt_assets': 'Total Debt/Total Assets',
        'debt_at': 'Total Debt/Total Assets',
        'debt_capital': 'Total Debt/Capital',
        'intcov': 'After-tax Interest Coverage',
        'intcov_ratio': 'Interest Coverage Ratio',
        'cash_conversion': 'Cash Conversion Cycle (Days)',
        'cash_ratio': 'Cash Ratio',
        'curr_ratio': 'Current Ratio',
        'quick_ratio': 'Quick Ratio (Acid Test)',
        'at_turn': 'Asset Turnover',
        'inv_turn': 'Inventory Turnover',
        'pay_turn': 'Payables Turnover',
        'rect_turn': 'Receivables Turnover',
        'sale_equity': 'Sales/Stockholders Equity',
        'sale_invcap': 'Sales/Invested Capital',
        'sale_nwc': 'Sales/Working Capital',
        'accrual': 'Accruals/Average Assets',
        'rd_sale': 'Research and Development/Sales',
        'adv_sale': 'Advertising Expenses/Sales',
        'staff_sale': 'Labor Expenses/Sales',
    }
    return metrics.get(metric_key, "Metric key not found")
