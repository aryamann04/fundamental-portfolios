import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

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

def plot_metric_return(df, metric):
    df_filtered = remove_outliers(df)
    plt.figure(figsize=(12, 6))
    sns.scatterplot(x='MetricValue', y='Return', data=df_filtered)

    slope, intercept, r_value, p_value, std_err = stats.linregress(df_filtered['MetricValue'], df_filtered['Return'])
    plt.plot(df_filtered['MetricValue'], intercept + slope * df_filtered['MetricValue'], color='red',
             label=f'Fit Line (R² = {r_value ** 2:.2f})')

    plt.xlabel(metric)
    plt.ylabel('Return')
    plt.title(f'{get_metric_description(metric)} vs. return')
    plt.legend()
    plt.grid(True)
    plt.show()

def remove_outliers(df, threshold=3):
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

if __name__ == "__main__":
    metric = 'bm'

    df = metric_and_return_df('nasdaq100', metric, '2014-06-30', '2024-06-30')
    plot_metric_return(df, metric)
