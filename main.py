from backtest import rebalanced_portfolio
from print import print_portfolio_stats, plot_portfolio_returns

#-------[parameters]-------#
metric = 'CAPEI'
start_date = '2008-09-30'
end_date = '2010-09-30'
index = 'russell200'
plot_granularity = 'quarterly'

"""
NOTE: Russell Top 200 portfolios show Russell 2000 (^RUT) as index on plot 

[NASDAQ 100] earliest start_date: 2000-06-01
[Russell 200] earliest start_date: 2008-09-30
[Russell 200] latest end_date: 2017-09-30

available metrics for portfolio construction:

1. dpr            (Float)  : Dividend Payout Ratio (dpr)
2. PEG_trailing   (Float)  : Trailing P/E to Growth (PEG) ratio (peg_trailing)
3. bm             (Float)  : Book/Market (bm)
4. CAPEI          (Float)  : Shillers Cyclically Adjusted P/E Ratio (capei)
5. divyield       (Float)  : Dividend Yield (divyield)
6. evm            (Float)  : Enterprise Value Multiple (evm)
7. pcf            (Float)  : Price/Cash flow (pcf)
8. pe_exi         (Float)  : P/E (Diluted, Excl. EI) (pe_exi)
9. pe_inc         (Float)  : P/E (Diluted, Incl. EI) (pe_inc)
10. pe_op_basic   (Float)  : Price/Operating Earnings (Basic, Excl. EI) (pe_op_basic)
11. pe_op_dil     (Float)  : Price/Operating Earnings (Diluted, Excl. EI) (pe_op_dil)
12. ps            (Float)  : Price/Sales (ps)
13. ptb           (Float)  : Price/Book (ptb)
14. efftax        (Float)  : Effective Tax Rate (efftax)
15. gprof         (Float)  : Gross Profit/Total Assets (gprof)
16. aftret_eq     (Float)  : After-tax Return on Average Common Equity (aftret_eq)
17. aftret_equity (Float)  : After-tax Return on Total Stockholders Equity (aftret_equity)
18. aftret_invcapx(Float)  : After-tax Return on Invested Capital (aftret_invcapx)
19. gpm           (Float)  : Gross Profit Margin (gpm)
20. npm           (Float)  : Net Profit Margin (npm)
21. opmad         (Float)  : Operating Profit Margin After Depreciation (opmad)
22. opmbd         (Float)  : Operating Profit Margin Before Depreciation (opmbd)
23. pretret_earnat(Float)  : Pre-tax Return on Total Earning Assets (pretret_earnat)
24. pretret_noa   (Float)  : Pre-tax return on Net Operating Assets (pretret_noa)
25. ptpm          (Float)  : Pre-tax Profit Margin (ptpm)
26. roa           (Float)  : Return on Assets (roa)
27. roce          (Float)  : Return on Capital Employed (roce)
28. roe           (Float)  : Return on Equity (roe)
29. capital_ratio (Float)  : Capitalization Ratio (capital_ratio)
30. equity_invcap (Float)  : Common Equity/Invested Capital (equity_invcap)
31. debt_invcap   (Float)  : Long-term Debt/Invested Capital (debt_invcap)
32. totdebt_invcap(Float)  : Total Debt/Invested Capital (totdebt_invcap)
33. invt_act      (Float)  : Inventory/Current Assets (invt_act)
34. rect_act      (Float)  : Receivables/Current Assets (rect_act)
35. fcf_ocf       (Float)  : Free Cash Flow/Operating Cash Flow (fcf_ocf)
36. ocf_lct       (Float)  : Operating CF/Current Liabilities (ocf_lct)
37. cash_debt     (Float)  : Cash Flow/Total Debt (cash_debt)
38. cash_lt       (Float)  : Cash Balance/Total Liabilities (cash_lt)
39. cfm           (Float)  : Cash Flow Margin (cfm)
40. short_debt    (Float)  : Short-Term Debt/Total Debt (short_debt)
41. profit_lct    (Float)  : Profit Before Depreciation/Current Liabilities (profit_lct)
42. curr_debt     (Float)  : Current Liabilities/Total Liabilities (curr_debt)
43. debt_ebitda   (Float)  : Total Debt/EBITDA (debt_ebitda)
44. dltt_be       (Float)  : Long-term Debt/Book Equity (dltt_be)
45. int_debt      (Float)  : Interest/Average Long-term Debt (int_debt)
46. int_totdebt   (Float)  : Interest/Average Total Debt (int_totdebt)
47. lt_debt       (Float)  : Long-term Debt/Total Liabilities (lt_debt)
48. lt_ppent      (Float)  : Total Liabilities/Total Tangible Assets (lt_ppent)
49. de_ratio      (Float)  : Total Debt/Equity (de_ratio)
50. debt_assets   (Float)  : Total Debt/Total Assets (debt_assets)
51. debt_at       (Float)  : Total Debt/Total Assets (debt_at)
52. debt_capital  (Float)  : Total Debt/Capital (debt_capital)
53. intcov        (Float)  : After-tax Interest Coverage (intcov)
54. intcov_ratio  (Float)  : Interest Coverage Ratio (intcov_ratio)
55. cash_conversion(Float) : Cash Conversion Cycle (Days) (cash_conversion)
56. cash_ratio    (Float)  : Cash Ratio (cash_ratio)
57. curr_ratio    (Float)  : Current Ratio (curr_ratio)
58. quick_ratio   (Float)  : Quick Ratio (Acid Test) (quick_ratio)
59. at_turn       (Float)  : Asset Turnover (at_turn)
60. inv_turn      (Float)  : Inventory Turnover (inv_turn)
61. pay_turn      (Float)  : Payables Turnover (pay_turn)
62. rect_turn     (Float)  : Receivables Turnover (rect_turn)
63. sale_equity   (Float)  : Sales/Stockholders Equity (sale_equity)
64. sale_invcap   (Float)  : Sales/Invested Capital (sale_invcap)
65. sale_nwc      (Float)  : Sales/Working Capital (sale_nwc)
66. accrual       (Float)  : Accruals/Average Assets (accrual)
67. rd_sale       (Float)  : Research and Development/Sales (rd_sale)
68. adv_sale      (Float)  : Advertising Expenses/Sales (adv_sale)
69. staff_sale    (Float)  : Labor Expenses/Sales (staff_sale)
"""

portfolios, portfolio_stats = rebalanced_portfolio(metric, index=index, start_date=start_date, end_date=end_date)
print_portfolio_stats(portfolio_stats)
plot_portfolio_returns(portfolios, start_date=start_date, end_date=end_date, granularity=plot_granularity, index=index)
