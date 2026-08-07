with source as (
    select * from {{ source('raw', 'events') }}
)
select
    event_id,
    customer_id,
    event_type,
    page,
    timestamp::timestamp as timestamp,
    product_id,
    price::numeric(10,2) as price
from source
