-- Historical USD/NGN rates loaded by Python.
-- Restore the Airbyte union after the custom connector works.

select
    cast(date as date) as rate_date,
    upper(trim(base)) as base,
    upper(trim(quote)) as quote,
    cast(rate as numeric(20,8)) as usd_ngn_rate
from {{ source('raw', 'exchange_rate_history') }}
where upper(trim(base)) = 'USD'
  and upper(trim(quote)) = 'NGN'
  and rate > 0
