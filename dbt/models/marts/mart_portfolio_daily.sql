select
    price_date,
    sum(position_value_usd) as total_value_usd,
    sum(total_cost_usd) as total_cost_usd,
    sum(unrealized_gain_loss_usd) as total_unrealized_gain_loss_usd,
    case when count(*)=count(position_value_ngn)
       then sum(position_value_ngn) else null end as total_value_ngn
from {{ ref('mart_portfolio_value') }}
group by price_date
