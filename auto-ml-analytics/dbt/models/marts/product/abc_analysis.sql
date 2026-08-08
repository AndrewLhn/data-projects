with product_sales as (
    select
        product_id,
        sum(total_price) as revenue
    from {{ ref('int_order_items_enriched') }}
    group by product_id
),
cumulative as (
    select
        product_id,
        revenue,
        sum(revenue) over (order by revenue desc) as cumulative_revenue,
        sum(revenue) over () as total_revenue,
        (sum(revenue) over (order by revenue desc)::float / sum(revenue) over ()) * 100 as cumulative_percent
    from product_sales
)
select
    product_id,
    revenue,
    cumulative_percent,
    case
        when cumulative_percent <= 80 then 'A'
        when cumulative_percent <= 95 then 'B'
        else 'C'
    end as abc_class
from cumulative
