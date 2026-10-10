-- Every valuation must reflect only purchases already made by that date.
select v.price_date,v.ticker,v.shares_held,
  (select sum(t.shares_bought) from {{ ref('stg_trades') }} t
   where t.ticker=v.ticker and t.trade_date<=v.price_date) as expected_shares
from {{ ref('mart_portfolio_value') }} v
where v.shares_held <> (
    select sum(t.shares_bought) from {{ ref('stg_trades') }} t
    where t.ticker=v.ticker and t.trade_date<=v.price_date
)
