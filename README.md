# fundamental-portfolios
[currently in progress]

This project is a portfolio construction tool that allows users to analyze stock portfolios based on various financial metrics. Users can rank stocks, perform backtesting, and visualize cumulative returns over time. The tool also provides detailed information about the tickers in each portfolio group, including their performance and financial metrics. The data ranges from `2000-06-01` to `2023-12-31`. Historical index constituents, fundamental metrics, and price data was acquired from CRSP and Compustat databases via Wharton Research Data Services. 

## Features

- Rank stocks based on financial metrics
- Perform backtesting on portfolios
- Visualize cumulative returns
- Detailed portfolio analysis including tickers, returns, and financial metrics

## Available Metrics

Below are the available metrics that you can use for your analysis:

- `dpr`            : Dividend Payout Ratio
- `peg_trailing`   : Trailing P/E to Growth (PEG) ratio
- `bm`             : Book/Market
- `capei`          : Shillers Cyclically Adjusted P/E Ratio
- `divyield`       : Dividend Yield
- `evm`            : Enterprise Value Multiple
- `pcf`            : Price/Cash flow
- `pe_exi`         : P/E (Diluted, Excl. EI)
- `pe_inc`         : P/E (Diluted, Incl. EI)
- `pe_op_basic`    : Price/Operating Earnings (Basic, Excl. EI)
- `pe_op_dil`      : Price/Operating Earnings (Diluted, Excl. EI)
- `ps`             : Price/Sales
- `ptb`            : Price/Book
- `efftax`         : Effective Tax Rate
- `gprof`          : Gross Profit/Total Assets
- `aftret_eq`      : After-tax Return on Average Common Equity
- `aftret_equity`  : After-tax Return on Total Stockholders Equity
- `aftret_invcapx` : After-tax Return on Invested Capital
- `gpm`            : Gross Profit Margin
- `npm`            : Net Profit Margin
- `opmad`          : Operating Profit Margin After Depreciation
- `opmbd`          : Operating Profit Margin Before Depreciation
- `pretret_earnat` : Pre-tax Return on Total Earning Assets
- `pretret_noa`    : Pre-tax return on Net Operating Assets
- `ptpm`           : Pre-tax Profit Margin
- `roa`            : Return on Assets
- `roce`           : Return on Capital Employed
- `roe`            : Return on Equity
- `capital_ratio`  : Capitalization Ratio
- `equity_invcap`  : Common Equity/Invested Capital
- `debt_invcap`    : Long-term Debt/Invested Capital
- `totdebt_invcap` : Total Debt/Invested Capital
- `invt_act`       : Inventory/Current Assets
- `rect_act`       : Receivables/Current Assets
- `fcf_ocf`        : Free Cash Flow/Operating Cash Flow
- `ocf_lct`        : Operating CF/Current Liabilities
- `cash_debt`      : Cash Flow/Total Debt
- `cash_lt`        : Cash Balance/Total Liabilities
- `cfm`            : Cash Flow Margin
- `short_debt`     : Short-Term Debt/Total Debt
- `profit_lct`     : Profit Before Depreciation/Current Liabilities
- `curr_debt`      : Current Liabilities/Total Liabilities
- `debt_ebitda`    : Total Debt/EBITDA
- `dltt_be`        : Long-term Debt/Book Equity
- `int_debt`       : Interest/Average Long-term Debt
- `int_totdebt`    : Interest/Average Total Debt
- `lt_debt`        : Long-term Debt/Total Liabilities
- `lt_ppent`       : Total Liabilities/Total Tangible Assets
- `de_ratio`       : Total Debt/Equity
- `debt_assets`    : Total Debt/Total Assets
- `debt_at`        : Total Debt/Total Assets
- `debt_capital`   : Total Debt/Capital
- `intcov`         : After-tax Interest Coverage
- `intcov_ratio`   : Interest Coverage Ratio
- `cash_conversion`: Cash Conversion Cycle (Days)
- `cash_ratio`     : Cash Ratio
- `curr_ratio`     : Current Ratio
- `quick_ratio`    : Quick Ratio (Acid Test)
- `at_turn`        : Asset Turnover
- `inv_turn`       : Inventory Turnover
- `pay_turn`       : Payables Turnover
- `rect_turn`      : Receivables Turnover
- `sale_equity`    : Sales/Stockholders Equity
- `sale_invcap`    : Sales/Invested Capital
- `sale_nwc`       : Sales/Working Capital
- `accrual`        : Accruals/Average Assets
- `rd_sale`        : Research and Development/Sales
- `adv_sale`       : Advertising Expenses/Sales
- `staff_sale`     : Labor Expenses/Sales

## Setup

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/aryamann04/fundamental-portfolios.git
   cd fundamental-portfolios
2. Install dependencies:
   ```bash
   pip install pandas matplotlib yfinance numpy datetime
   
