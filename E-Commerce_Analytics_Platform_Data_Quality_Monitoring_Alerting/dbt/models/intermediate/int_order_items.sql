select
    o.order_id,
    o.customer_id,
    o.order_date,
    i.product_id,
    i.quantity,
    i.unit_price,
    i.quantity * i.unit_price as line_total
from {{ ref('stg_orders') }} o
join {{ ref('stg_order_items') }} i on o.order_id = i.order_id
