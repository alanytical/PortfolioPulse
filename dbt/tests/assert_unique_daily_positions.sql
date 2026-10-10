-- Fail if a ticker has multiple valuations on the same day.
select price_date,ticker,count(*) from {{ ref('mart_portfolio_value') }}
group by price_date,ticker having count(*) > 1
