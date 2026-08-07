with source as (
    select * from {{ source('raw', 'customers') }}
)
select
    customer_id,
    email,
    signup_date::timestamp as signup_date,
    country,
    city,
    age
from source
