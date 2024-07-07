import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import statsmodels.api as sm

from datapipeline import price, historical_data
from print import get_metric_description

def metric_and_return_df(index, metric, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    metrics_data = historical_data(start_date, index)
    results = []

    for ticker in metrics_data['TICKER'].unique():
        metric_value = metrics_data[metrics_data['TICKER'] == ticker][metric].values[0]

        price_data = price(ticker, start_date, end_date, index)
        if price_data is not None:
            start_price = price_data.loc[price_data.index[price_data.index <= start_date].max(), 'prccd']
            end_price = price_data.loc[price_data.index[price_data.index <= end_date].max(), 'prccd']

            stock_return = (end_price / start_price) - 1
            results.append({'Ticker': ticker, 'MetricValue': metric_value, 'Return': stock_return})

    results_df = pd.DataFrame(results).dropna()
    return results_df

def regression(index, metrics, start_date, end_date):
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)
    metrics_data = historical_data(start_date, index)
    results = []

    for ticker in metrics_data['TICKER'].unique():
        metric_values = {}
        for metric in metrics:
            metric_value = metrics_data[metrics_data['TICKER'] == ticker][metric].values[0]
            metric_values[metric] = metric_value

        price_data = price(ticker, start_date, end_date, index)
        if price_data is not None:
            start_price = price_data.loc[price_data.index[price_data.index <= start_date].max(), 'prccd']
            end_price = price_data.loc[price_data.index[price_data.index <= end_date].max(), 'prccd']

            stock_return = (end_price / start_price) - 1
            metric_values['Return'] = stock_return
            results.append(metric_values)

    results_df = pd.DataFrame(results).dropna()
    results_df = remove_outliers(results_df)
    X = sm.add_constant(results_df[metrics])
    y = results_df['Return']

    model = sm.OLS(y, X)
    results = model.fit()

    print(results.summary())
    return results_df

def plot_metric_return(df, metric):
    df_filtered = remove_outliers(df)
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='MetricValue', y='Return', data=df_filtered)

    X = sm.add_constant(df_filtered['MetricValue'])
    model = sm.OLS(df_filtered['Return'], X)
    results = model.fit()

    plt.plot(df_filtered['MetricValue'], results.fittedvalues, color='red',
             label=f'Fit Line (R² = {results.rsquared:.2f})')

    plt.xlabel(get_metric_description(metric))
    plt.ylabel('Return')
    plt.title(f'{get_metric_description(metric)} vs. return')
    plt.legend()
    plt.grid(True)
    plt.show()

    print(results.summary())

def remove_outliers(df, threshold=2):
    q1_metric = df['MetricValue'].quantile(0.25)
    q3_metric = df['MetricValue'].quantile(0.75)
    iqr_metric = q3_metric - q1_metric
    lower_bound_metric = q1_metric - threshold * iqr_metric
    upper_bound_metric = q3_metric + threshold * iqr_metric

    q1_return = df['Return'].quantile(0.25)
    q3_return = df['Return'].quantile(0.75)
    iqr_return = q3_return - q1_return
    lower_bound_return = q1_return - threshold * iqr_return
    upper_bound_return = q3_return + threshold * iqr_return

    df_filtered = df[(df['MetricValue'] >= lower_bound_metric) & (df['MetricValue'] <= upper_bound_metric) &
                     (df['Return'] >= lower_bound_return) & (df['Return'] <= upper_bound_return)]

    return df_filtered

def perform_regressions(index, start_date, end_date):
    results_list = []
    metrics = ['CAPEI', 'bm', 'evm', 'pe_op_basic', 'pe_op_dil', 'pe_exi', 'pe_inc', 'ps', 'pcf', 'dpr', 'npm',
               'opmbd', 'opmad', 'gpm', 'ptpm', 'cfm', 'roa', 'roe', 'roce', 'efftax', 'aftret_eq', 'aftret_invcapx',
               'aftret_equity', 'pretret_noa', 'pretret_earnat', 'GProf', 'equity_invcap', 'debt_invcap',
               'totdebt_invcap', 'capital_ratio', 'int_debt', 'int_totdebt', 'cash_lt', 'invt_act', 'rect_act',
               'debt_at', 'debt_ebitda', 'short_debt', 'curr_debt', 'lt_debt', 'profit_lct', 'ocf_lct', 'cash_debt',
               'fcf_ocf', 'lt_ppent', 'dltt_be', 'debt_assets', 'debt_capital', 'de_ratio', 'intcov', 'intcov_ratio',
               'cash_ratio', 'quick_ratio', 'curr_ratio', 'cash_conversion', 'inv_turn', 'at_turn', 'rect_turn',
               'pay_turn', 'sale_invcap', 'sale_equity', 'sale_nwc', 'rd_sale', 'adv_sale', 'staff_sale', 'accrual',
               'ptb', 'PEG_trailing']
    for metric in metrics:
        print(metric)
        df = metric_and_return_df(index, metric, start_date, end_date)
        df = remove_outliers(df)

        if df.empty:
            continue

        X = sm.add_constant(df['MetricValue'])
        y = df['Return']
        model = sm.OLS(y, X)
        results = model.fit()

        results_list.append({'Metric': metric, 'P-Value': results.pvalues['MetricValue'],
                             'R-Squared': results.rsquared, 'Coefficient': results.params['MetricValue'],
                             'n': results.nobs})

    results_df = pd.DataFrame(results_list)
    results_df = results_df.sort_values(by='R-Squared', ascending=False)

    return results_df

if __name__ == "__main__":
    metric = 'npm'
    df = metric_and_return_df('nasdaq100', metric, '2021-06-30', '2023-06-30')
    plot_metric_return(df, metric)
    
    pd.set_option('display.max_rows', None)
    
    df1 = perform_regressions('nasdaq100', '2023-06-30', '2024-06-30')
    print("1yr")
    print(df1)
    df2 = perform_regressions('nasdaq100', '2022-06-30', '2024-06-30')
    print("2yr")
    print(df2)
    df3 = perform_regressions('nasdaq100', '2021-06-30', '2024-06-30')
    print("3yr")
    print(df3)
    df4 = perform_regressions('nasdaq100', '2020-06-30', '2024-06-30')
    print("4yr")
    print(df4)
    df5 = perform_regressions('nasdaq100', '2019-06-30', '2024-06-30')
    print("5yr")
    print(df5)
    df10 = perform_regressions('nasdaq100', '2014-06-30', '2024-06-30')
    print("10yr")
    print(df10)
