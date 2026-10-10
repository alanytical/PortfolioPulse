-- The Google Sheets source emits strings, so explicit casting is necessary.
-- Set Airbyte trade_log sync to FULL REFRESH / OVERWRITE.
select
    trim(trade_id) as trade_id,
    cast(trade_date as date) as trade_date,
    upper(trim(ticker)) as ticker,
    cast(shares_bought as numeric(18,6)) as shares_bought,
    cast(price_paid as numeric(18,6)) as price_paid
from {{ source('raw','trade_log') }}
where nullif(trim(trade_id),'') is not null
