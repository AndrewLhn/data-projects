with source as (
    select * from {{ source('raw', 'order_items') }}
),
renamed as (
    select
        item_id,
        order_id,
        product_id,
        quantity::int as quantity,
        unit_price::numeric(10,2) as unit_price
    from source
)
select * from renamed
