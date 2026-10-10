-- A dated position is the sum of buys made on or before that price date.
-- This cohort example intentionally contains ONLY buy transactions (no sells).
-- NGN value remains NULL before the first actual FX observation; no invented rates.
with priced_holdings as (
    select
        p.price_date, p.ticker, p.close_usd,
        sum(t.shares_bought) as shares_held,
        sum(t.shares_bought * t.price_paid) as total_cost_usd
    from {{ ref('stg_stock_prices') }} p
    inner join {{ ref('stg_trades') }} t
        on p.ticker=t.ticker and t.trade_date<=p.price_date
    group by p.price_date,p.ticker,p.close_usd
), value_usd as (
    select *, shares_held*close_usd as position_value_usd,
        shares_held*close_usd-total_cost_usd as unrealized_gain_loss_usd
    from priced_holdings
)
select
    v.price_date, v.ticker, v.close_usd,
    v.shares_held, v.total_cost_usd,
    v.position_value_usd, v.unrealized_gain_loss_usd,
    fx.usd_ngn_rate,
    v.position_value_usd*fx.usd_ngn_rate as position_value_ngn
from value_usd v
left join lateral (
    select r.usd_ngn_rate from {{ ref('stg_exchange_rates') }} r
    where r.rate_date<=v.price_date
    order by r.rate_date desc limit 1
) fx on true
