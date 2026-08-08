with funnel_steps as (
    select
        customer_id,
        max(case when event_type = 'view' then timestamp end) as view_time,
        max(case when event_type = 'add_to_cart' then timestamp end) as cart_time,
        max(case when event_type = 'purchase' then timestamp end) as purchase_time
    from {{ ref('stg_events') }}
    group by customer_id
)
select
    count(distinct customer_id) as total_customers,
    count(distinct case when view_time is not null then customer_id end) as views,
    count(distinct case when cart_time is not null then customer_id end) as carts,
    count(distinct case when purchase_time is not null then customer_id end) as purchases,
    (count(distinct case when cart_time is not null then customer_id end)::float / count(distinct customer_id)) * 100 as view_to_cart_rate,
    (count(distinct case when purchase_time is not null then customer_id end)::float / count(distinct case when cart_time is not null then customer_id end)) * 100 as cart_to_purchase_rate
from funnel_steps
