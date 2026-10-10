select
    cast(price_date as date) as price_date,
    upper(trim(ticker)) as ticker,
    cast(close_usd as numeric(18,6)) as close_usd,
    cast(volume as bigint) as volume
from {{ source('raw','stock_prices') }}
where close_usd > 0
