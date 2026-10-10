-- Fail if invalid trade amounts exist.
select * from {{ ref('stg_trades') }} where shares_bought <= 0 or price_paid <= 0
