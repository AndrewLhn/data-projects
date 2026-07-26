with source as (
    select * from {{ source('raw', 'orders') }}
),
renamed as (
    select
        order_id,
        customer_id,
        order_date::timestamp as order_date,
        status,
        total_amount::numeric(10,2) as total_amount
    from source
)
select * from renamed
