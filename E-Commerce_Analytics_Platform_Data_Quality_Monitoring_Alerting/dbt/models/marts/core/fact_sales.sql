select
    order_id,
    customer_id,
    order_date,
    sum(line_total) as total_revenue,
    count(distinct product_id) as unique_products
from {{ ref('int_order_items') }}
group by order_id, customer_id, order_date
