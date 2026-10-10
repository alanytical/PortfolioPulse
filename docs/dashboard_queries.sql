-- In Metabase: connect Neon and use the following datasets.
-- CHART 1: Line plot date vs USD (and NGN if a separate visualization)
select price_date,total_value_usd,total_value_ngn from analytics.mart_portfolio_daily order by price_date;
-- CHART 2: Bar chart latest gain/loss per stock
select ticker,unrealized_gain_loss_usd from analytics.mart_latest_positions order by unrealized_gain_loss_usd desc;
-- CHART 3: Donut allocation by ticker
select ticker,position_value_usd from analytics.mart_latest_positions order by position_value_usd desc;
-- CHART 4: Table displaying current USD & NGN side by side
select ticker,position_value_usd,position_value_ngn,allocation_pct from analytics.mart_latest_positions order by ticker;
