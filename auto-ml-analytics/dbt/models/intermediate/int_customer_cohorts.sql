with first_orders as (
    select
        customer_id,
        min(order_date) as first_order_date,
        date_trunc('month', min(order_date)) as cohort_month
    from {{ ref('stg_orders') }}
    group by customer_id
)
select * from first_orders
