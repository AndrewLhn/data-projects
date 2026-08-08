with customer_orders as (
    select
        customer_id,
        count(distinct order_id) as total_orders,
        avg(total_price) as avg_order_value,
        sum(total_price) as lifetime_value,
        min(order_date) as first_order_date,
        max(order_date) as last_order_date,
        date_part('day', max(order_date) - min(order_date)) as customer_lifetime_days
    from {{ ref('int_order_items_enriched') }}
    group by customer_id
),
recency as (
    select
        customer_id,
        date_part('day', current_date - max(order_date)) as recency_days
    from {{ ref('stg_orders') }}
    group by customer_id
)
select
    co.customer_id,
    co.total_orders,
    co.avg_order_value,
    co.lifetime_value,
    co.first_order_date,
    co.last_order_date,
    co.customer_lifetime_days,
    r.recency_days,
    date_part('month', age(co.last_order_date, co.first_order_date)) + 1 as active_months
from customer_orders co
left join recency r on co.customer_id = r.customer_id
