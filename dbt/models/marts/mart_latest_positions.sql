with latest_day as (select max(price_date) as price_date from {{ ref('mart_portfolio_value') }})
select v.*, v.position_value_usd / nullif(
       sum(v.position_value_usd) over(),0) * 100 as allocation_pct
from {{ ref('mart_portfolio_value') }} v
inner join latest_day d on v.price_date=d.price_date
