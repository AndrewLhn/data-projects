with source as (
    select * from {{ source('raw', 'order_items') }}
)
select
    item_id,
    order_id,
    product_id,
    quantity::int as quantity,
    unit_price::numeric(10,2) as unit_price,
    total_price::numeric(10,2) as total_price
from source
