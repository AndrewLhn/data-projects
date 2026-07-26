select
    date_trunc('day', order_date) as sales_day,
    count(distinct order_id) as orders_count,
    sum(line_total) as revenue,
    avg(line_total) as avg_order_value
from {{ ref('int_order_items') }}
group by 1
order by 1
